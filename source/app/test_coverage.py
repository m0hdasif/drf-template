from coverage import Coverage


class UnitTestCoverage:
    def __init__(self) -> None:
        """Initiate test coverage."""
        self.cov = Coverage()

    def run(self):
        self.cov.erase()
        self.cov.start()

    def stop(self):
        self.cov.stop()
        self.cov.save()
        self.cov.report()
