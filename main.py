import re
import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
# 仅保留Service导入（用于指定本地驱动），移除webdriver-manager
from selenium.webdriver.chrome.service import Service

print("===== 脚本开始执行 =====")

# 防止打印一些无用的日志
option = webdriver.ChromeOptions()
# 基础反检测
option.add_experimental_option("excludeSwitches", ['enable-automation','enable-logging'])
option.add_experimental_option('useAutomationExtension', False)
option.add_argument('--disable-blink-features=AutomationControlled')
# 解决Chrome启动崩溃的核心参数
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage')
option.add_argument('--remote-debugging-port=9222')
# 自定义用户数据目录（桌面路径，权限充足）
profile_dir = r"C:\Users\ASUS\Desktop\ChromeProfile"
if not os.path.exists(profile_dir):
    os.makedirs(profile_dir)
    print(f"✅ 创建用户数据目录：{profile_dir}")
option.add_argument(f'--user-data-dir={profile_dir}')
option.add_argument('--start-maximized')
# 强制显示Chrome窗口（避免静默启动）
option.add_argument('--force-app-mode')

print("✅ 配置Chrome参数完成")

# 1. 手动指定 Chrome 浏览器完整路径（已确认有效）
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
option.binary_location = chrome_path
if os.path.exists(chrome_path):
    print(f"✅ Chrome路径有效：{chrome_path}")
else:
    print(f"❌ Chrome路径无效：{chrome_path}")
    print("⚠️  请检查路径是否正确！")
    sys.exit()

# 2. 手动指定本地 ChromeDriver 路径（核心！不用自动下载）
# 驱动路径：脚本同目录的 chromedriver.exe
driver_path = r"C:\Users\ASUS\Desktop\ZaiQiHang-AutoLearn-main\chromedriver.exe"
if not os.path.exists(driver_path):
    print(f"❌ 本地驱动不存在：{driver_path}")
    print("⚠️  请确认chromedriver.exe已放在脚本文件夹里！")
    sys.exit()
# 创建Service对象，指向本地驱动
service = Service(executable_path=driver_path)
print(f"✅ 本地驱动路径有效：{driver_path}")

# 3. 启动Chrome（使用本地驱动）
print("🚀 开始启动Chrome浏览器...")
try:
    driver = webdriver.Chrome(service=service, options=option)
    print("✅ Chrome启动成功")
except Exception as e:
    print(f"❌ Chrome启动失败！错误原因：{str(e)}")
    print("⚠️  请检查驱动版本是否匹配Chrome 140，或驱动路径是否正确！")
    sys.exit()

# 访问目标网站
print("🌐 开始访问网站：https://www.mvazqh.org.cn/")
driver.get("https://www.mvazqh.org.cn/")
print("✅ 网站访问完成，等待用户登录...")

# 等待用户登录并定位到课程页面
wait = WebDriverWait(driver, 120, 2)
try:
    print("🔍 等待定位课程页面元素 [data-status='1']...")
    alert = wait.until(presence_of_element_located((By.CSS_SELECTOR, '[data-status="1"]')))
    print("✅ 已定位到课程页面元素，用户已登录")
except:
    print('❌ 120秒内未登录/未切换到课程页面，刷课失败')
    driver.quit()
    sys.exit()

# 现已成功到达课程页面
print("🔄 切换到未完成课程标签...")
try:
    driver.find_element(By.CSS_SELECTOR, '[data-status="0"]').click()
    time.sleep(5)
    print("✅ 切换未完成课程成功")
except Exception as e:
    print(f"❌ 切换未完成课程失败：{str(e)}")

while True:
    print("🔍 开始展开所有课程详情...")
    try:
        for knowns in driver.find_elements(By.CLASS_NAME, 'known'):
            knowns.click()
        print("✅ 展开课程详情成功")
    except:
        print('❌ 展开详情失败！')
        pass
    
    time.sleep(5)
    
    courses = driver.find_elements(By.CLASS_NAME, 'course-learning-progress')
    print(f"📚 当前页面课程数量：{len(courses)}")
    if len(courses) == 0:
        print("✅ 页面无课程，结束循环")
        break
    
    num = 0
    while num < len(courses):
        try:
            learned_progress = float(courses[num].find_element(
                By.CLASS_NAME, 'learned-section-num').text[:-1])
            if learned_progress < 100:
                print(f"🔍 选择第{num}门课（进度{learned_progress}%）开始学习")
                break
        except:
            print(f"❌ 读取第{num}门课进度失败，跳过")
        num += 1
    
    if num >= len(courses):
        print("✅ 所有课程已学完，结束循环")
        break
    
    course_detail = courses[num]
    try:
        progress = course_detail.find_element(By.CLASS_NAME, 'learned-section-num').text
        if float(progress[:-1]) >= 100:
            continue
        course_detail.find_element(By.CLASS_NAME, 'required-course-play').click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        print("✅ 打开课程播放页面成功")
    except Exception as e:
        print(f"❌ 打开课程失败：{str(e)}")
        driver.switch_to.window(driver.window_handles[0])
        continue
    
    try:
        driver.implicitly_wait(5)
        title = driver.find_element(By.CLASS_NAME, 'first_title').get_attribute('innerText')
        print(f'🎬 开始学习课程《{title}》')
        print('当前进度：', end='', flush=True)
    except:
        print('🎬 开始学习下一门课程')
        pass
    
    try:
        driver.execute_script("document.getElementById(\"showInfo\").style.display='block';")
        info = driver.find_element(By.ID, 'showInfo')
    except:
        print("❌ 无法定位进度条，跳过进度显示")
        continue
    
    milestone = 0
    percent = 0
    while percent < 100:
        try:
            percent = int(re.findall(r'\d+', info.text)[0])
            if percent // 10 * 10 > milestone:
                milestone = percent // 10 * 10
                print(f"{milestone}% ", end='', flush=True)
        except:
            print("❌ 读取进度失败，重试...")
            time.sleep(2)
            continue
        time.sleep(10)
    
    print('100%')
    print('✅ 课程已学习完毕。\n')
    time.sleep(2)
    
    try:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.refresh()
        time.sleep(2)
        print("✅ 关闭课程页，返回课程列表")
    except Exception as e:
        print(f"❌ 切换标签页失败：{str(e)}")
        # 重新启动Chrome时，复用本地驱动路径
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=option)
        driver.get("https://www.mvazqh.org.cn/")
        time.sleep(5)

print('🎉 所有课程学习完毕！')
driver.quit()