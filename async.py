"""
Builds types found in files, folders etc.
Current solution is asynchronous to be independent
of order.
TODO better to create a static tree that can be analyzed?
"""
from config_template import discover, read_from_yaml
import asyncio
import logging
import collections
import tqdm

logger = logging.getLogger()


class DependencyTree(object):
    """Pretty ugly, probably can do nicer"""
    def __init__(self):
        self.dependencies = collections.defaultdict(set)

    def add_down(self, typ, dependency):
        # type depends on dependency and its childs
        if typ in dependency:
            raise ValueError("cycle")
        for d in self.dependencies[dependency]:
            if d in self.dependencies[typ]:
                continue
            self.dependencies[typ].add(d)
            self.add_down(typ, d)

    def add_up(self, typ, dependency):
        # types that depend on this type also depend on dependancy
        if typ == dependency:
            raise ValueError("cycle")
        for d in self.dependencies:
            if typ in d:
                if dependency in self.dependencies[d]:
                    continue
                self.dependencies[d].add(dependency)
                self.add_up(typ, d)

    def add(self, typ, dependency):
        self.dependencies[typ].add(dependency)
        self.add_down(typ, dependency)
        self.add_up(typ, dependency)


class TypeFactory(object):
    def __init__(self):
        self.started_types = set()
        self.finished_types = set()
        self.available_types = set(['int', 'string', 'bool', 'float'])

        self.registered_cfgs = {}

        self.tasks = []
        self.events = collections.defaultdict(asyncio.Event)

        self.types = {}
        self.dependecy_tree = DependencyTree()

    def register_type(self, name, type):
        self.types[name] = type

    def register_cfg(self, name, cfg):
        self.registered_cfgs[name] = cfg

    def register_directory(self, name, path):
        self.directories[name] = path

        for path, name in discover('descriptors'):
            print("found {} {}".format(name, path))

    def register_file(self, name, path):
        if path.endswith('.yaml'):
            cfg = read_from_yaml(path)
        else:
            raise ValueError("Unknown File Ending")

        if cfg is None:
            logger.warning("Skipping %s (%s)", name, path)
            return
        self.register_cfg(name, cfg)

    def build_directories(self):
        for name, directory in self.register_directories.items():
            event = self.events.pop(name, None)
            if event is not None:
                event.set()
        self.available_types.add(name)

    # we have a cycle if a type has dependcies that depend on the type
    # its easier to pass down dependcies of parent
    async def build_type(self, name, cfg, events):
        tasks = []
        print("Start building {}".format(name))
        for key, value in cfg.items():
            if value['type'] == 'datatype' and value['dtype'] not in self.types:
                dependency = value['dtype']
                self.dependecy_tree.add(name, dependency)
                # we must wait for the type to be available
                # is someone else already waiting
                event = self.events[dependency]
                waiter_task = asyncio.create_task(wait(dependency, event))
                # error when the dependency depends on this
        # wait for all dependencies to solve
        print(dependencies)
        await asyncio.gather(*tasks)
        # now build type
        if name in events:
            event = events.pop(name)
            event.set()
        available_types.add(name)
        finished_types.add(name)
        print("finished {}".format(name))

    def build_types(self):
        for name, cfg in self.cfg.items():
            self.started_types.add(name)
            task = asyncio.create_task(self.build_type(name, cfg))
            self.tasks.append(task)

    async def _build(self):
        print("discovered {}".format(len(started_types)))
        print(len(started_types), len(finished_types))
        print(started_types, finished_types)
        counter = 0
        pbar = tqdm.tqdm(total=len(started_types))
        curr = 0
        MAX_WAIT_T = 5
        not_finished = started_types - finished_types
        while len(not_finished) != 0:
            pbar.write("finished so far {}".format(finished_types))
            pbar.write("Not finished {}".format(not_finished))
            pbar.update(len(finished_types) - curr)
            curr = len(finished_types)
            await asyncio.sleep(1)
            not_finished = started_types - finished_types
            counter += 1
            if counter == MAX_WAIT_T:
                raise ValueError("One type seems not to finish")
                break
        print("finished")


    def build(self):
        loop = asyncio.get_event_loop()
        loop.run_until_completion(self._build())
        loop.close()
