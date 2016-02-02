import aiohttp
import aiohttp.helpers
import email.mime.multipart
import email.mime.text
import markdown
import io


class Mailgun(object):
    def __init__(self, domain, api_key):
        self.domain = domain
        self.api_key = api_key

    async def _request(self, method, endpoint, data):
        return (await aiohttp.request(
            method,
            'https://api.mailgun.net/v3/{domain}/{endpoint}'.format(
                domain=self.domain,
                endpoint=endpoint),
            auth=aiohttp.BasicAuth('api', self.api_key),
            data=data))

    async def send(self, to, message, **kwargs):
        form_data = aiohttp.helpers.FormData(kwargs)
        if isinstance(to, str):
            to = [to]

        for v in to:
            form_data.add_field('to', v)

        form_data.add_field('message', io.StringIO(message.as_string()))

        req = await self._request('POST', 'messages.mime', form_data)
        resp = (await req.json())

        if req.status != 200:
            raise ValueError(resp['message'])
        else:
            return resp


def make_markdown_email(text, headers, **kwargs):
    msg = email.mime.multipart.MIMEMultipart('alternative')

    for k, v in headers.items():
        msg[k] = v

    msg.attach(email.mime.text.MIMEText(text, 'plain'))
    msg.attach(email.mime.text.MIMEText(markdown.markdown(text, **kwargs),
                                        'html'))
    return msg
