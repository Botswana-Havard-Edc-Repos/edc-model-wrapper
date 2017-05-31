from collections import OrderedDict
from django.urls.base import reverse
from urllib import parse


class NextUrlError(Exception):
    pass


class Keywords(OrderedDict):

    def __init__(self, objects=None, attrs=None, include_attrs=None, **kwargs):
        super().__init__()
        if include_attrs:
            attrs = [attr for attr in attrs if attr in include_attrs]
        for attr in attrs:
            value = None
            for obj in objects:
                if value:
                    break
                try:
                    value = getattr(obj, attr)
                except AttributeError:
                    value = None
            self.update({attr: value or ''})


class NextUrlParser:

    """A class to set `next_url`.

    `next_url` is  a qyerystring that follows the format of edc_base model
        admin mixin for redirecting the model admin on save
        to a url other than the default changelist.
        * Note: This is not a url but parameters need to reverse
                to one in the template.

    User is responsible for making sure the url_name can be reversed
    with the given parameters.

    In your url &next=my_url_name,arg1,arg2&agr1=value1&arg2=
    value2&arg3=value3&arg4=value4...etc.

    * next_url_attrs:
        A dict with a list of querystring attrs to include in the next url.

        Format is:
            {key1: [param1, param2, ...], key2: [param1, param2, ...]}

    """
    keywords_cls = Keywords

    def __init__(self, url_name=None, url_args=None, url_namespace=None, **kwargs):
        if not url_name:
            raise NextUrlError(f'Invalid url_name. Got {url_name}')
        self.url_name = url_name
        self.url_args = url_args
        self.url_namespace = url_namespace

    def querystring(self, objects=None, **kwargs):
        if self.url_args:
            url_namespace = f'{self.url_namespace}:' if self.url_namespace else ''
            next_args = ',{}'.format(','.join(self.url_args))
            url_kwargs = {
                k: v for k, v in kwargs.items() if k in (self.url_args or [])}
            keywords = self.keywords_cls(
                objects=objects, attrs=self.url_args, include_attrs=self.url_args, **url_kwargs)
            querystring = parse.urlencode(keywords, encoding='utf-8')
            return f'next={url_namespace}{self.url_name}{next_args}&{querystring}'
        return ''

#     def reverse(self):
#         return reverse(self.url_name, kwargs=self._next_kwargs)