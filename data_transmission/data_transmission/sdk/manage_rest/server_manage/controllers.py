"""
manage http controller package
"""
from ....sdk.http import wsgi
from ....sdk.server_manager import Manager


class ManageController(wsgi.V3Controller):
    """manage http controller implement class.

    所属单元: 数据获取提取单元

    """

    name = 'name desc'

    def __init__(self, *args, **kw):
        """
        init func
        """
        super(ManageController, self).__init__(*args, **kw)

    def tests(self, request):
        """
        implement /tests url controller function
        :param request: http request
        """
        # body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.tests()
        return result

    def info(self, request):
        """
        implement / or /info or empty url controller function
        :param request: http request
        """
        # body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.info()
        return result

    def start(self, request):
        """
        implement /manage/start url controller function
        :param request: http request
        """
        body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.start(body)
        Manager.the_instance.status = 'running'
        return result

    def stop(self, request):
        """
        implement /manage/stop url controller function
        :param request: http request
        """
        body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.stop(body)
        Manager.the_instance.status = 'stopped'
        return result

    def restart(self, request):
        """
        implement /manage/restart url controller function
        :param request: http request
        """
        # body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.restart()
        Manager.the_instance.status = 'running'
        return result

    def update(self, request):
        """
        implement /update url controller function
        :param request: http request
        """
        # body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.update(request)
        return result

    def process_start(self, request):
        """
        implement /manage/start url controller function
        :param request: http request
        """
        body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.process_start(body)
        Manager.the_instance.status = 'running'
        return result

    def process_stop(self, request):
        """
        implement /manage/stop url controller function
        :param request: http request
        """
        body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.process_stop(body)

        Manager.the_instance.status = 'stopped'
        return result

    def test_connect(self, request):
        """
        implement /manage/test_connect url controller function
        :param request: http request
        """
        body = request.json
        # result = self.test_service_api.tests()
        result = Manager.the_instance.test_connect(body)
        Manager.the_instance.status = 'test'
        return result