# XSSnium

`XSSnium` is a tool for testing Cross-Site Scripting (XSS) vulnerabilities by injecting a list of payloads into URLs with parameters. It uses Selenium for automated browser interaction, so you'll need `chromedriver` installed to use it.
<br>
After making the Parameter-grabber script I made this because it just made sense.

## What does this script do?
The script takes a text file containing a list of XSS payloads and combines them with a list of URLs that include parameters. For instance, if you have:
- A file named `payloads.txt` with a payload like `<script>alert('XSS')</script>`
- A file named `URL.txt` containing `https://example.com?example=`

The script will then generate requests to `https://example.com?example=<script>alert('XSS')</script>` using both GET and POST methods. This approach allows you to automate the testing of multiple payloads across different URLs, potentially uncovering XSS vulnerabilities.

You will be sending `N°_of_Payloads x N°_of_URLS x 2` requests in total (the x2 is because it sends both GET and POST).

## Requirements
- `Selenium`
- `chromedriver` (ensure it matches your Chrome version)

## Usage
Use this script to test for XSS vulnerabilities by including payloads that point to an XSSHunter URL or other XSS detection mechanisms.

```
python script.py <target_urls_file_path> <payload_file_path>
```

## Note
Ensure `chromedriver` is properly installed and accessible in your system's PATH.
