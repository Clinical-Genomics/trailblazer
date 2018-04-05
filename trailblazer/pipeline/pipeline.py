import logging
import signal
import subprocess

LOG = logging.getLogger(__name__)

class Pipeline(object):

    def __init__(self, script):
        """Initialize command line interface."""
        self.script = script

    def start(self, family, config=None, **kwargs):
        """Execute the pipeline."""
        command = self.build_command(config, family=family, **kwargs)
        LOG.debug(' '.join(command))
        process = self.execute(command)
        process.wait()
        if process.returncode != 0:
            raise PipelineStartError('error starting analysis, check the output')
        return process

    def build_command(self, **kwargs):
        """Build the command."""
        command = [self.script]
        for key, value in kwargs.items():
            command.append(key)
            command.append(value)
        return command

    def execute(self, command):
        """Start a new run."""
        process = subprocess.Popen(
            command,
            preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        )
        return process
