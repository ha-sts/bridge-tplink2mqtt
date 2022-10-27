#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
# class MethodTickler:
#     def __init__(self):
#         self.logger = logging.getLogger(type(self).__name__)
#         self._corofuncs = []
#         self._stop = False
#
#     def add_corofunc(self, corofunc):
#         # NOTE: The coroutine generating method supplied should not require arguments
#         #       For later improvement: https://stackoverflow.com/a/65755581
#         self._corofuncs.append(corofunc)
#
#     def stop(self):
#         self._stop = True
#
#     async def run(self):
#         while not self._stop:
#             self.logger.debug("Tickling 'em Heartbeats")
#             cororuns = []
#             for i in self._corofuncs:
#                 cororuns.append(i())
#             await asyncio.gather(*cororuns)
#             await asyncio.sleep(300) # Every five minutes for now.

class MethodTickler:
    def __init__(self, seconds, corofunc):
        self.logger = logging.getLogger(type(self).__name__)
        # NOTE: The coroutine generating method supplied should not require arguments
        #       For later improvement: https://stackoverflow.com/a/65755581
        self._seconds = seconds
        self._corofunc = corofunc
        self._stop = False

    def stop(self):
        self._stop = True

    async def run(self):
        while not self._stop:
            self.logger.debug("Tickling the method: %s", self._corofunc)
            asyncio.create_task(self._corofunc())
            await asyncio.sleep(self._seconds)
