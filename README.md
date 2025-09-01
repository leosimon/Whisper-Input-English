# Whisper Input

Whisper Input is a simple Python tool inspired by [FeiTTT](https://web.okjike.com/u/DB98BE7A-9DBB-4730-B6B9-2DC883B986B1). Hold the Option key to start recording and release it to stop. It uses Groq's `Whisper Large V3 Turbo` model for transcription. Thanks to Groq's speed, most speech inputs return within 1–2 seconds, and Whisper provides excellent transcription quality.

- 🎉🎉A more user-friendly speech input app, [WhisperKeyBoard](https://whisperkeyboard.app/), is now available. I highly recommend using it directly. The focus of Whisper Input will continue to shift back to Voice + Agents.

## Features

| Feature        | Shortcut                        |
| -------------- | ------------------------------- |
| Multilingual Speech-to-Text | Option or Alt                 |
| Chinese → English Translation | Shift + Option or Shift + Alt |



Watch the [demo video](https://img.erlich.fun/personal-blog/uPic/WhisperInputV02_compressed.mp4)



**Note: Both Groq and SiliconFlow offer sufficient free quotas. No payment or credit card required.**


## Usage

> Currently two free ASR models are supported: Groq-hosted `Whisper Large V3 series` and SiliconFlow-hosted `FunAudioLLM/SenseVoiceSmall` series. If you are outside mainland China, choose Groq.

### Prerequisites
Please ensure you have a local Python environment, with Python version 3.10 or higher.
#### Python 3.13.1 has a known issue causing errors when switching window focus. No fix yet. Python 3.12.5 works without this error.

### FunAudioLLM/SenseVoiceSmall Setup
1. Register a SiliconFlow account: https://cloud.siliconflow.cn/i/RXikvHE2
2. Create and copy a free API KEY: https://cloud.siliconflow.cn/account/ak
3. Open the terminal and navigate to the folder where you want to download the project
    ```bash
    git clone git@github.com:ErlichLiu/Whisper-Input.git
    ```
4. Create a virtual environment (recommended)
    ```bash
    python -m venv venv
    ```

5. Rename the `.env` file
    ```bash
    cp .env.example .env
    ```

6. Paste the API KEY from step 2 into the `.env` file, for example:
    ```bash
    SERVICE_PLATFORM=siliconflow
    SILICONFLOW_API_KEY=sk_z8q3rXrQM3o******************8dQEJCYz3QTJQYZ
    ```

7. In a terminal session you plan to keep open, navigate to the project folder and activate the virtual environment
    ```bash
    # macOS / Linux
    source venv/bin/activate
    
    # Windows
    .\venv\Scripts\activate
    ```

8. Install dependencies
    ```bash
    pip install pip-tools
    pip-compile requirements.in
    pip install -r requirements.txt
    ```

9. Run the program
    ```bash
    python main.py
    ```


### Groq Whisper Large V3 Setup
1. Register a Groq account: https://console.groq.com/login
2. Copy a free Groq API KEY: https://console.groq.com/keys
3. Open the terminal and navigate to the folder where you want to download the project
    ```bash
    git clone git@github.com:ErlichLiu/Whisper-Input.git
    ```
4. Create a virtual environment (recommended)
    ```bash
    python -m venv venv
    ```

5. Rename the `.env` file
    ```bash
    cp .env.example .env
    ```

6. Paste the API KEY from step 2 into the `.env` file, for example:
    ```bash
    SERVICE_PLATFORM=groq
    GROQ_API_KEY=gsk_z8q3rXrQM3o******************8dQEJCYz3QTJQYZ
    ```

7. In a terminal session you plan to keep open, navigate to the project folder and activate the virtual environment
    ```bash
    # macOS / Linux
    source venv/bin/activate
    
    # Windows
    .\venv\Scripts\activate
    ```

8. Install dependencies
    ```bash
    pip install pip-tools
    pip-compile requirements.in
    pip install -r requirements.txt
    ```

9. Run the program
    ```bash
    python main.py
    ```

    

**🎉  You can now hold the Option key to start speech input!**



![image-20250111140954085](https://img.erlich.fun/personal-blog/uPic/image-20250111140954085.png)

## Tips

This program needs to keep running in the background. It's best to run it in a terminal window or tab that you won't accidentally close.



Follow the author's website for more projects: https://erlich.fun