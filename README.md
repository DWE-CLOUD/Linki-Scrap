# Linkedin-scrap [ The Anonymous Api for Scrapping ] BETA

Since this is in its Beta Release do note that some profiles might not load due to Skills tab issue aka " SKILL ISSUE XD " .. This would be there for some and for some it should work Fine .. This uses the binary approach to the Linkedin By Bypassing the Login Authwalls and the Blank Li Redirects and Re Captcha V3 invisible by simulating it directly from the Script side and the Xpath controllers .

So in brief : 

An advanced LinkedIn profile scraper that bypasses authentication walls and detection systems to collect profile information anonymously.

## IMPORTANT

- While Entering the link it should be like this : www.linkedin.com/in/ohri-akshit/
- Like it should have : www.linkedin.com/{your_country_code}/{your_profile_id}/
- The / in end is imp

## 🚀 Features

- Anonymous scraping with authentication bypass
- 2FA-enabled account support
- Modified ChromeDriver for undetectable automation
- Advanced CSS and XPath selectors for reliable data extraction
- Dynamic ID generation handling
- Precise profile information extraction
- Docker support for containerized execution

## ⚠️ Disclaimer

This tool is in BETA. Some profiles might experience scraping issues which will be addressed in future updates.

## 🛠️ Installation

### Docker (Recommended)
```bash
# build the image
docker build -t linkedin-scrapper .

# Run the container
docker run -d -p 8000:8000 --env-file .env linkedin-scrapper
```

### Local Installation
```bash
# Clone the repository
git clone https://github.com/DWE-CLOUD/Linki-scrap

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

1. Edit the `.env` file:
```yaml
linkedin:
  username: your_email
  password: your_password
  ```

## 🚀 Usage

```python

#chrome_options.add_argument('--headless')  Uncomment this line for running the image
```

Also When running it , the path should be changed as well on this line 

```
service = Service(executable_path='/usr/local/bin/chromedriver')

```

## 📊 Output Format


Example of my link:

```json
{
  "name": "Akshit Ohri",
  "about": "Passionate about pushing the boundaries of what's possible through code, I thrive on turning ambitious ideas into reality. As a dedicated coder, my expertise lies in crafting innovative and cutting-edge projects that challenge the status quo. Specializing in the dynamic realms of cybersecurity and artificial intelligence, I am committed to staying ahead of the curve in the ever-evolving tech landscape.\n\nWith a keen eye for detail and a penchant for problem-solving, I have successfully translated complex concepts into tangible solutions, making the seemingly unrealistic not only achievable but also impactful. My journey in the world of technology has been marked by a relentless pursuit of excellence, from designing robust cybersecurity frameworks to harnessing the power of AI for transformative applications.\n\nJoin me on this exciting journey where creativity meets functionality, and where the intersection of coding, cybersecurity, and AI opens doors to unprecedented possibilities. Let's connect, collaborate, and innovate as we navigate the digital frontier together.",
  "work_experience": [
    {
      "title": "Founder",
      "company": "Snugs Official · Self-employed",
      "duration": "Nov 2024 - Present · 2 mos",
      "location": "India · Hybrid",
      "about": "Building Snugs, a dating app focused on genuine connections through warmth, playfulness, and inclusivity. Passionate about creating a community-first platform where people connect over shared values and real relationships."
    },
    {
      "title": "Head of Web Development",
      "company": "IEEE Computer Society SRMIST · Part-time",
      "duration": "Sep 2024 - Present · 4 mos",
      "location": "India · Hybrid",
      "about": "Leading web development teams to deliver innovative, scalable, and high-performance web solutions.\nLeading web development teams to deliver innovative, scalable, and high-performance web solutions."
    },
    {
      "title": "Project Intern",
      "company": "SRM Technologies · Internship",
      "duration": "May 2024 - Present · 8 mos",
      "location": "Hybrid"
    },
    {
      "title": "Technical Team Member",
      "company": "Data Science Community SRM · Part-time",
      "duration": "Oct 2023 - Present · 1 yr 3 mos",
      "location": "India"
    },
    {
      "title": "Member",
      "company": "Next Tech Lab",
      "duration": "Nov 2023 - May 2024 · 7 mos",
      "location": "Hybrid",
      "about": "Satoshi Lab\nSatoshi Lab"
    }
  ],
  "education": [
    {
      "institution": "SRMIST, Kattankulathur, Chennai ,Tamil Nadu",
      "degree": "2023 - 2027"
    },
    {
      "institution": "DAV International School, Kharghar",
      "degree": "High school, PCMCS",
      "duration": "2014 - 2023"
    }
  ],
  "skills": [
    "Flutter",
    "Dart",
    "Kotlin",
    "Start-up Leadership",
    "Social Emotional Learning",
    "Public Relations",
    "WebDev",
    "React.js",
    "Next.js",
    "TypeScript",
    "Ethical Hacking",
    "ML",
    "Machine Learning",
    "Deep Learning",
    "Go lang",
    "Cybersecurity",
    "Python (Programming Language)",
    "Programming"
  ],
  "license": [
    "Introduction to Cybersecurity",
    "Google Hash Code",
    "INTEL AI FOR YOUTH",
    "Intel Digital Readiness",
    "ETHICAL HACKING IIT B"
  ]
}
```

## ⚙️ Technical Details

- Uses modified ChromeDriver binaries
- Implements advanced detection bypass mechanisms
- Handles dynamic element IDs
- Employs smart waiting strategies
- Uses hybrid CSS/XPath selectors


## 🚫 Known Issues

- Some profiles may fail to scrape completely

## 📝 License

MIT License

## ⚠️ Legal Notice

This tool is for educational purposes only. Use at your own risk and responsibility. Ensure compliance with LinkedIn's terms of service in your jurisdiction.

## 🤝 Contributing

Feel free to submit issues and enhancement requests! 
