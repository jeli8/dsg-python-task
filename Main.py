from PIL import Image
from selenium import webdriver
import io
import boto3
import settings

def uploadFileToS3(fileName):
    s3 = boto3.client('s3',
                 aws_access_key_id=settings.S3_ACCESS_KEY,
                 aws_secret_access_key=settings.S3_SECRET_KEY)
    s3.upload_file(fileName, settings.S3_BUCKET_NAME, fileName)
    print("File uploaded successfully!")

def main():
    DRIVER = 'chromedriver'
    chrome = webdriver.Chrome(DRIVER)
    chrome.get(settings.URL)

    verbose = 1

    js = 'return Math.max( document.body.scrollHeight, ' \
         'document.body.offsetHeight,  document.documentElement.clientHeight,  ' \
         'document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

    scrollheight = chrome.execute_script(js)

    slices = []
    offset = 0
    while offset < scrollheight:
        chrome.execute_script("window.scrollTo(0, %s);" % offset)
        img = Image.open(io.BytesIO(chrome.get_screenshot_as_png()))
        offset += img.size[1]
        slices.append(img)

        if verbose > 0:
            chrome.get_screenshot_as_file('%s/screen_%s.png' % ('/tmp', offset))

    slice_height = sum([slice.size[1] for slice in slices])
    screenshot = Image.new('RGB', (slices[0].size[0], slice_height))
    offset = 0
    for img in slices:
        screenshot.paste(img, (0, offset))
        offset += img.size[1]

    outputFile = settings.OUTPUT_FILE_NAME + ".png"
    screenshot.save(outputFile)
    uploadFileToS3(outputFile)

    chrome.quit()
    return 0


if __name__ == "__main__":
    main()