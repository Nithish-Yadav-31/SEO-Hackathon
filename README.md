# SEO-Hackathon

Workflow:
![archi updated](https://github.com/user-attachments/assets/0cc77522-3837-428f-90e7-92a409ced52e)


# Running the SEO Hackathon Application

This guide outlines the steps required to set up and run the SEO Hackathon application.

## Prerequisites

Before you begin, ensure that you have the following installed:

  **Python:** Python 3.8 or higher. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
*   **Conda (Recommended):** Conda is a package and environment manager. It can be downloaded from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html).  Using Conda is highly recommended for managing dependencies.
*   **Git (Optional):** Git is a version control system. It is useful for cloning the project repository. It can be downloaded from [https://git-scm.com/downloads](https://git-scm.com/downloads).

## Setup Instructions

### 1. Clone the Repository (If Applicable)

If you have the code in a Git repository, clone it to your local machine:

```bash
git clone <repository_url>
cd <project_directory>
```

Replace `<repository_url>` with the URL of your project's Git repository and `<project_directory>` with the name of the directory where the project is cloned.

### 2. Create and Activate a Conda Environment (Recommended)

It's best practice to create a separate Conda environment for your project to isolate its dependencies:

```
conda create --name seo-hackathon python=3.9  # Creates an environment named "seo-hackathon"
conda activate seo-hackathon          # Activates the "seo-hackathon" environment
```

Replace `"seo-hackathon"` with a name of your choice.

### 3. Install Dependencies

Use `pip` to install the required Python packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command reads the `requirements.txt` file and installs all the listed packages and their specific versions.  If you encounter issues during installation, ensure that your Conda environment is activated and that you have the correct version of `pip` installed within the environment.

### 4. Configure API Keys

This application uses several APIs that require API keys:

*   **Google Gemini API:**  You will need to obtain a Google Gemini API key to use the `intent_analyser.py`, `compare_intent.py`, `missing_topic_finder.py` and `query_writer.py` components.
*    **DuckDuckGo API:** This is used in search_competitor.py, it doesnt require API keys

Create a `.env` file in the root directory of the project (the same directory as `app.py`).  Add the following lines to the `.env` file, replacing `<YOUR_API_KEY>` with your actual API keys:

```
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
```

### 5. Run the Flask Application

Once you have installed the dependencies and configured the API keys, you can run the Flask application:

```
python app.py
```

This will start the Flask development server. You should see output similar to this:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### 6. Access the Application

Open your web browser and navigate to the URL provided in the output (usually `http://127.0.0.1:5000/`). You should now be able to interact with the application.

## Usage

1.  In your web browser, enter the website URL you want to analyze in the provided form.
2.  Submit the form.
3.  The application will process the website, extract relevant information, and display the results.
