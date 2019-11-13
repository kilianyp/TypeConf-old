from config_template import discover, read_from_yaml
import asyncio
import logging
import collections

logger = logging.getLogger()
available_types = set(['int', 'string', 'bool', 'float'])

dependencies = collections.defaultdict(set)

async def wait(name, event):
    print("waiting on dependcy {name}".format(name=name))
    # TODO is this safe or better mutex
    await event.wait()
    print("Done waiting for {name}".format(name=name))


def add_down(typ, dependency):
    # type depends on dependency and its childs
    if typ in dependency:
        raise ValueError("cycle")
    for d in dependencies[dependency]:
        if d in dependencies[typ]:
            continue
        dependencies[typ].add(d)
        add_down(typ, d)


def add_up(typ, dependency):
    # types that depend on this type also depend on dependancy
    if typ == dependency:
        raise ValueError("cycle")
    for d in dependencies:
        if typ in d:
            if dependency in dependencies[d]:
                continue
            dependencies[d].add(dependency)
            add_up(typ, d)

# we have a cycle if a type has dependcies that depend on the type
# its easier to pass down dependcies of parent
async def build_type(name, cfg, events):
    tasks = []
    print("Start building {}".format(name))
    for key, value in cfg.items():
        if value['type'] == 'datatype' and value['dtype'] not in available_types:
            dependency = value['dtype']
            # loops are only now critical
            dependencies[name].add(dependency)
            add_up(name, dependency)
            add_down(name, dependency)
            # we must wait for the type to be available
            # is someone else already waiting
            if dependency in events:
                event = events[dependency]
            else:
                event = asyncio.Event()
                events[dependency] = event
            waiter_task = asyncio.create_task(wait(dependency, event))
            # error when the dependency depends on this
            tasks.append(waiter_task)
    # wait for all dependencies to solve
    print(dependencies)
    await asyncio.gather(*tasks)
    # now build type
    if name in events:
        event = events.pop(name)
        event.set()
    available_types.add(name)
    print("finished {}".format(name))


async def main():
    events = {}
    tasks = []

    # WARNING if nested types take too long this will not work
    started_types = set()

    for path, name in discover('descriptors'):
        print("found {} {}".format(name, path))
        if path.endswith('.yaml'):
            cfg = read_from_yaml(path)
            if cfg is None:
                logger.warning("Skipping %s (%s)", name, path)
                continue
            started_types.add(name)
            task = asyncio.create_task(build_type(name, cfg, events))
            tasks.append(task)
        else:
            if name in events:
                event = events.pop(name)
                event.set()
            print("adding {}".format(name))
            available_types.add(name)
            # continue

    not_finished = started_types - available_types
    counter = 0
    while len(not_finished) != 0:
        print("finished so far", available_types)
        print("Not finished", not_finished)
        await asyncio.sleep(1)
        not_finished = started_types - available_types
        counter += 1
        if counter == 5:
            raise ValueError("One type seems not to finish")
            break
    print("finished")

asyncio.run(main())


