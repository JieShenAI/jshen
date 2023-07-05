import os
import pathlib
import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from typing import Union, Sequence
from ..io import json2dict


# reforence: https://blog.csdn.net/Cameback_Tang/article/details/122540118
class Email:
    """
    settings_file:
        {
            "user":"xxxrobot@163.com",
            "pwd":"xxxxxxxxx",
            "host":"smtp.163.com",
            "receiver":"接收人@qq.com"
        }

    """

    def __init__(self, settings_file):
        self.__settings = json2dict(settings_file)
        self.sender = self.__settings['user']
        # 传递给Header的From的参数，随便写都可以;
        # 格式必须为: "your_name@xx.域名" 或 your_name<your_name@xx.域名>
        self.from_addr = "noreply@cn.world"
        self.receiver = self.__settings['receiver']
        self.__connect()
        self.rear_text = "\n\n\t    此邮件由机器人发送，您无法直接回复。"

    def __connect(self):
        host = self.__settings['host']
        password = self.__settings['pwd']
        print('Info: Enter Email ... ')
        self.__smtp_obj = smtplib.SMTP_SSL(host, port=465)  # 根据是否ssl认证进行二选一
        try:
            # 连接到服务器
            # self._smtpObj.connect(host=self._mail_host, port=25)
            self.__smtp_obj.connect(host=host, port=465)
            # 登录到服务器
            res = self.__smtp_obj.login(user=self.sender, password=password)
            print(f'登录结果：{res}')
        except smtplib.SMTPException as e:
            print("163 email login failed with error: %s" % e)  # 打印错误
        finally:
            return self  # 注意enter里面一定要返回类的对象self,否则无法调用run方法。

    def email_send(self, to_addrs, message):
        '''
        # 邮件发送
        :param to_addrs: 包含所有收件人的列表
        :param message: 邮件格式化的字符串，或邮件对象
        如 message = '\n'.join(['From: {}'.format(FROM), 'To: {}'.format(TO), 'Subject: {}'.format(SUBJECT), '', CONTENT])
        :return:
        '''

        try:
            self.__smtp_obj.sendmail(from_addr=self.sender, to_addrs=to_addrs, msg=str(message))
            print("邮件投递成功")
            return True
        except Exception as e:
            print("email 投递失败: %s" % e.args)  # 打印错误
            return False

    def textMail_send(self,
                      to_addrs=[],
                      cc_addrs=[],
                      bcc_addrs=[],
                      subject='robot',
                      content=''
                      ):

        '''
            发送字符串等正文文本信息，使用 MIMEText 对象，不能附件
            :param from_addr: 其实只是别名，效果：XXXXX@163.com on behalf of xxxxxx@163.com
            :param to_addrs: 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
            :param cc_addrs: 抄送人列表
            :param bcc_addrs: 秘密抄送人列表
            :param title: 邮件标题
            :param content: 邮件内容
            :return:
        '''
        ## 1、邮件正文文本信息，可以使用 MIMEText 对象
        # 实例化简单邮件对象，邮件正文内容设置
        # 若_text参数传递了文本字符串，则_subtype参数应该传递’plain’。
        # 若_text参数传递了二进制文件，则_subtype参数应该传递’base64’。
        msg = MIMEText(content + self.rear_text, 'plain', 'utf-8')

        # 2、设置设置邮件信息：邮件主题、发送人、收件人、抄送、秘密抄送
        # 我们使用三个引号来设置邮件信息，标准邮件需要三个头部信息：
        # From, To, 和 Subject ，每个信息直接使用空行分割。
        from email.header import Header
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['To'] = ";".join(to_addrs)
        msg['Cc'] = ",".join(cc_addrs)
        msg['Bcc'] = ";".join(bcc_addrs)

        # 3、给 所有收件人 send email
        addressees = to_addrs + cc_addrs + bcc_addrs
        return self.email_send(to_addrs=addressees, message=msg)

    def demo(self, to_addrs=[]):
        """
        简化的发送邮件的例子
        :param to_addrs:
        :return:
        """
        msg = "\n".join([
            'From:js<jie@cn.world>',
            f'To:{";".join(to_addrs)}',
            'Subject:Test',
            '',
            'no <>'
        ])
        self.__smtp_obj.sendmail(self.sender, to_addrs, msg)

    def add_image_attachment(self,
                             multiMsg,
                             filePath,
                             filenameInEmail=None):
        '''
            添加照片附件
            :param multiMsg: MIMEMultipart()，实例化复合邮件对象
            :param filePath: 文件路径：需要检查 filePath 是否存在
            :param filenameInEmail: 邮件中的附件命名，默认None即使用filePath中的文件名字
            :return:
            '''

        assert os.path.exists(filePath), f'找不到附件：{filePath}'

        if not filenameInEmail:
            filenameInEmail = os.path.basename(filePath)

        print(f'添加附件：{filenameInEmail}')
        # 发送utf-8的文件名
        filenameInEmail = Header(filenameInEmail, 'utf-8').encode()
        with open(filePath, 'rb') as fp:
            picture = MIMEImage(
                fp.read(),
                _subtype='octet-stream',  # 二进制流
            )

            picture['Content-Type'] = 'application/octet-stream'  # 附件设置内容类型，方便起见，设置为二进制流
            picture['Content-Disposition'] = f'attachment; filename="{filenameInEmail}"'  # 附件命名
            multiMsg.attach(picture)
        return multiMsg

    def add_text_attachment(self,
                            multiMsg,
                            filePath,
                            filenameInEmail=None):
        '''
            添加文本附件
            :param multiMsg: MIMEMultipart()，实例化复合邮件对象
            :param filePath: 文件路径：需要检查 filePath 是否存在 todo
            :param filenameInEmail: 邮件中的附件命名，默认None即使用filePath中的文件名字
            :return:
        '''

        assert os.path.exists(filePath), f'找不到附件：{filePath}'

        if not filenameInEmail:
            filenameInEmail = os.path.basename(filePath)

        # # 添加文件附件
        with open(filePath, 'rb') as f:
            # 以二进制读入文件，创建文本邮件对象
            file_data = MIMEText(f.read(), 'base64', 'utf-8')
            file_data['Content-Type'] = 'application/octet-stream'  # 附件设置内容类型，方便起见，设置为二进制流
            file_data['Content-Disposition'] = f'attachment; filename="{filenameInEmail}"'  # 附件命名
            multiMsg.attach(file_data)  # 添加附件到复合邮件对象中, attach一次只能放一个简单邮件对象
        return multiMsg

    def add_application(self, multiMsg,
                        filename: Union[pathlib.Path, str, Sequence[pathlib.Path], Sequence[str]]
                        ):
        """
        :reference: https://blog.csdn.net/xiaolipanpan/article/details/112461566
        :return:
        """
        if isinstance(filename, (pathlib.Path, str)):
            txtfile = MIMEApplication(open(filename, 'rb').read())
            filename = os.path.basename(filename)
            filename = Header(filename, 'utf-8').encode()
            txtfile.add_header('Content-Disposition', 'attachment', filename=filename)
            multiMsg.attach(txtfile)
        # elif isinstance(filename, Sequence):
        else:
            for file in filename:
                print(f'添加附件：{file}')
                txtfile = MIMEApplication(open(file, 'rb').read())
                filename = os.path.basename(file)
                filename = Header(filename, 'utf-8').encode()
                txtfile.add_header('Content-Disposition', 'attachment', filename=filename)
                multiMsg.attach(txtfile)
        return multiMsg

    def multiTypeMailer_send(self,
                             from_addr='',
                             to_addrs=[],
                             cc_addrs=[],
                             bcc_addrs=[],
                             subject='robot',
                             mail_html_msg='',  # 可输入文本支持html格式
                             attachments: Union[Sequence[pathlib.Path], Sequence[str]] = None):
        '''
            发送带附件的邮件，首先要创建 MIMEMultipart()实例，然后构造附件，如果有多个附件，可依次构造，
            :param from_addr: 其实只是别名，效果：XXXXX@163.com on behalf of xxxxxx@163.com
            :param to_addrs: 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
            :param cc_addrs: 抄送人列表
            :param bcc_addrs: 秘密抄送人列表
            :param title: 邮件标题
            :param mail_html_msg: 邮件内容
            :param attachments: 附件路径列表
            :return:
            '''
        # 1、构造MIMEMultipart对象作为根容器
        # 实例化复合邮件对象。它可以用来装载多个简单邮件对象
        msg = MIMEMultipart()

        # # 3、邮件正文
        # 推荐使用html格式的正文内容，这样比较灵活，可以附加图片地址，调整格式等。    # 添加HTML内容, 三双引号
        # 可以使用 MIMEMultipart 对象，也可以使用 MIMEText 对象， 并添加正文到复合邮件对象中
        msgContent = MIMEMultipart()
        msg.attach(msgContent)

        mail_html_msg += self.rear_text
        msgContent.attach(MIMEText(mail_html_msg, 'html', 'utf-8'))

        # # 4、邮件附件，读取附件内容， 注意以“二进制读”方式读取 文本、图片、音频
        if attachments:
            for attachment in attachments:
                basename = os.path.basename(attachment)
                attachment_type = basename.split('.')[-1]  # 如'image1.png'為 image1

                if attachment_type in ['txt', 'csv', 'xlsx', 'py']:
                    msg = self.add_text_attachment(msg, filePath=attachment)
                # elif attachment_type in ['png', 'jpg']:
                else:
                    msg = self.add_image_attachment(msg, filePath=attachment)
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['to'] = ";".join(to_addrs)
        msg['Cc'] = ";".join(cc_addrs)
        msg['Bcc'] = ";".join(bcc_addrs)
        addressees = to_addrs + cc_addrs + bcc_addrs
        return self.email_send(message=msg, to_addrs=addressees)


if __name__ == '__main__':
    home = pathlib.Path.home()
    p = home.joinpath(".xxxxxx/../settings.json")
    email = Email(p)
    msg = MIMEMultipart()
    msg.attach(MIMEText("hello world", 'html', 'utf-8'))
    msg['Subject'] = "Subject"
    msg['From'] = email.from_addr
    msg['to'] = ";".join(["xxx@qq.com"])
    email.email_send(message=msg, to_addrs=["xxx@qq.com"])

    # email.textMail_send(to_addrs=["xxx@qq.com", "15271895270@163.com"],
    #                     # cc_addrs=[""],
    #                     # bcc_addrs=[],
    #                     subject='robot',
    #                     content='机器人群发邮')
    # img_home = pathlib.Path(r"C:\Users\jshen\Pictures\MiHoYo")
    # imgs = [str(img) for img in img_home.glob("*.pkl")]

    # msgContent = MIMEMultipart()
    # home = pathlib.Path(r"C:\Users\jshen\Pictures\MiHoYo")
    # files = home.glob("*")
    # email.add_application(msgContent, filename=files)
    # email.email_send(message=msgContent, to_addrs=["xxx@qq.com"])

    # email.multiTypeMailer_send(
    #     to_addrs=["xxx@qq.com"],
    #     subject='robot',
    #     attachments=imgs)
