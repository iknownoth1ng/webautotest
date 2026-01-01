from time import sleep

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.core.base_page import BasePage


class ArticlePage(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)

    # 文章loc
    click_article_loc = (By.ID, "group-article")
    # 文章管理loc
    click_article_manage_loc = (By.ID, "文章管理--/admin/article/list")
    # 添加文章按钮loc
    click_add_article_btn_loc = (By.XPATH, "//a[contains(text(),'新建')]")

    # 文章标题
    article_title_loc = (By.ID, "article-title")

    # iframe loc
    iframe_loc = (By.XPATH, "//iframe")

    # body loc
    body_loc = (By.XPATH, "//div[@id='editor']/..//p")

    # 添加按钮
    add_btn_loc = (By.XPATH, "//button[contains(text(),'发布')]")

    # 文章链接
    article_link_loc = (
        By.XPATH,
        "/html/body/div/div/section[3]/div/div/div/div[2]/table/tbody/tr[2]/td[2]/strong/a",
    )

    # 删除文章链接
    del_article_link_loc = (
        By.XPATH,
        "/html/body/div/div/section[3]/div/div/div/div[2]/table/tbody/tr[2]/td[2]/div/div/a[3]",
    )

    # 文章loc
    select_all_checkbox_loc = (
        By.XPATH,
        "/html/body/div/div/section[3]/div/div/div/div[2]/table/tbody/tr[1]/th[1]/input",
    )

    # 删除所有按钮
    del_all_btn_loc = (By.ID, "batchDel")

    # 点击文章
    def click_article(self):
        self.click(self.click_article_loc)

    # 点击文章管理
    def click_article_manage(self):
        self.click(self.click_article_manage_loc)

    # 点击添加文章
    def click_add_article(self):
        self.click(self.click_add_article_btn_loc)

    # 输入文章标题
    def input_article_title(self, title):
        self.input_text(self.article_title_loc, title)

    # 输入body
    def input_body(self, body):
        # frame1 = self.find_element(*self.iframe_loc)
        # self.driver.switch_to.frame(frame1)
        self.input_text(self.body_loc, body)
        # self.driver.switch_to.default_content()

    # 点击添加
    def click_add_btn(self):
        self.click(self.add_btn_loc)

    # 删除单个文章
    def del_single_article(self):
        # 点击删除文章
        link = self.find_element(self.article_link_loc)
        ActionChains(self.driver).move_to_element(link).perform()

        del_elem = self.find_element(self.del_article_link_loc)
        del_elem.click()

    # 删除所有文章
    def del_all_article(self):
        sleep(1)
        self.find_element(self.click_article_manage_loc).click()
        sleep(1)

        link = self.find_element(self.select_all_checkbox_loc)
        link.click()

        self.find_element(self.del_all_btn_loc).click()

        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.accept()
