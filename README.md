# bridge-tplink2mqtt
Bridge for controlling tplink switches and plugs via MQTT.

NOTE: Due to changes in a couple of libraries, this now requires Python 3.8+.

FIXME: Had to force the versions of the python-kasa and aiomqtt libraries as updates have broken my usage of them.

FIXME: Need a more graceful way to handle shutting down the program.  Currently on a CTRL+C:
```
Traceback (most recent call last):
  File "/usr/pkg/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/pkg/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/fbus/bridge-tplink2mqtt/run.py", line 42, in wrapper
    await asyncio.gather(*tasks)
  File "/home/fbus/bridge-tplink2mqtt/hasts/bridges/tplink2mqtt/methodtickler.py", line 51, in run
    await asyncio.sleep(self._seconds)
  File "/usr/pkg/lib/python3.11/asyncio/tasks.py", line 649, in sleep
    return await future
           ^^^^^^^^^^^^
asyncio.exceptions.CancelledError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/fbus/bridge-tplink2mqtt/run.py", line 98, in <module>
    main()
  File "/home/fbus/bridge-tplink2mqtt/run.py", line 95, in main
    asyncio.run(wrapper(args))
  File "/usr/pkg/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/pkg/lib/python3.11/asyncio/runners.py", line 123, in run
    raise KeyboardInterrupt()
KeyboardInterrupt
```
