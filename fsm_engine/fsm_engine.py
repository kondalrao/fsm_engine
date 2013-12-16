__author__ = 'Kondal Rao Komaragiri'
import multiprocessing
import select
import logging
import fsm

TIMEOUT = 5000


class FsmEngine(object):

    def __init__(self, dispatch=None, flags=None):
        self.fsm_object_dict = {}
        self.dispatch = dispatch
        self.flags = flags
        self.logger = None
        self.rfd = []

        self.__engineStarted = False

        self.__init_log()

    def __init_log(self):
        # multiprocessing.log_to_stderr(logging.DEBUG)
        multiprocessing.log_to_stderr()
        self.logger = multiprocessing.get_logger()
        self.logger.setLevel(logging.CRITICAL)

    def __idle(self):
        # self.logger.debug("FsmEngine.__idle")
        pass

    def __collect_stats(self):
        # self.logger.debug("FsmEngine.__collectStats")
        pass

    def generate_fsm_id(self):
        self.logger.debug("FsmEngine.__getNewFSMId")
        fsm_id = [0]
        for obj in self.fsm_object_dict.values():
            if obj.obj_type == fsm.FSMQ:
                fsm_id.append(obj.fsm.getId())

        new_fsm_id = max(fsm_id) + 1
        self.logger.debug("FsmEngine.__getNewFSMId: new_fsm_id: %d" % new_fsm_id)

    def __register(self, fsm_object):
        self.fsm_object_dict[fsm_object.fd] = fsm_object
        self.rfd.append(fsm_object.fd)

    def __unregister(self, fsm_object):
        self.fsm_object_dict.pop(fsm_object.fd)
        self.rfd.remove(fsm_object.fd)

    def add_fsm(self, fsm_inst):
        self.logger.info("FsmEngine.addFSM: Adding FSM %s" % fsm_inst.fsm_name)

        # Check if the fsm_id is already present in the fsmEngine
        if fsm_inst.get_id() == -1:
            fsm_inst.set_id(self.generate_fsm_id())

        # for fsm_object in fsm.get_fsm_objects():
        #    self.add_fsm_object(fsm_object)

        map(self.add_fsm_object, fsm_inst.get_fsm_objects())

        fsm_inst.set_fsm_engine(self)
        fsm_inst.generate_initial_event()

    def remove_fsm(self, fsm_inst):
        self.logger.info("FsmEngine.addFSM: Adding FSM %s" % fsm_inst.fsm_name)
        map(self.del_fsm_object, fsm_inst.get_fsm_objects())

    def add_fsm_object(self, fsm_object):
        self.__register(fsm_object)

    def del_fsm_object(self, fsm_object):
        self.__unregister(fsm_object)

    def start_engine(self):
        self.logger.info("Starting fsm engine")

        self.__engineStarted = True

        while True:
            try:
                rfdl, wfdl, errfdl = select.select(self.rfd, [], [], TIMEOUT)
            except KeyboardInterrupt:
                exit()

            self.__collect_stats()

            if len(rfdl) == 0:
                self.__idle()
                continue

            # TODO: sort the events based on priority

            for fd in rfdl:
                self.logger.debug("fsmEngine.start_engine: fd: %s" % fd)
                fsm_object = self.fsm_object_dict[fd]

                if callable(fsm_object.dispatch_func):
                    fsm_object.dispatch_func(fsm_object)
