# Cloud-Based Media Content Search and Automated Tagging System for Nonprofits

Cloud-based solution with AI-driven tagging, content-based search, and integration capabilities with existing tools


## How to Run

Setup `.dev.env`
```bash
export WEBPAGE_URL='http://localhost'
export PG_HOST=localhost
export PG_PORT=5555
export PG_USER=postgres
export PG_PASSWORD=postgres
export PG_DB=peec_db
export FASTAPI_SESSION_SECRET_KEY=harsh
export DROPBOX_CLIENT_ID=
export DROPBOX_CLIENT_SECRET=
export OPENAI_API_KEY=
export TOGETHER_API_KEY=
export BATCH_WINDOW_TIME_SECS=10  # 10 secs
export GARBAGE_COLLECTION_TIME_SECS=600  # 10 mins
export POLL_WINDOW_TIME_SECS=10  # 10 secs
```

-- `.prod.env`
```bash
export WEBPAGE_URL='https://peec.harora.lol'
export PG_HOST=
export PG_PORT=
export PG_USER=
export PG_PASSWORD=
export PG_DB=
export FASTAPI_SESSION_SECRET_KEY=
export DROPBOX_CLIENT_ID=
export DROPBOX_CLIENT_SECRET=
export OPENAI_API_KEY=
export TOGETHER_API_KEY=
export BATCH_WINDOW_TIME_SECS=60  # 1 min
export GARBAGE_COLLECTION_TIME_SECS=3600  # 1 hr
export POLL_WINDOW_TIME_SECS=60  # 1 min
```

0. Add below to nginx.conf and restart:
    ```
        server {
            listen       80;
            server_name  localhost;
            client_max_body_size 100M;

            location /api/v1 {
                proxy_pass http://localhost:8081;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
            }
            location / {
                proxy_pass http://localhost:5173;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
            }
        }
    ```
1. Start PG DB
    ```bash
    source .dev.env
    cd backend/database
    docker compose up
    ```
2. Start React server
    2.0: Change in `frontend/web_app/src/api/api.jsx` to `axios.defaults.baseURL = 'http://localhost/api';`
    2.1: Start server
        ```bash
        cd frontend/web_app
        npm install
        npm run dev
        ```
3. Start FastAPI server
    ```bash
    cd backend
    conda env create -f env.yaml
    conda activate peec_env
    python -m uvicorn api:app --host localhost --port 8081 --reload
    ```

# Index

2. [Contributors](#contributors)
3. [Quick Preview & Links](#quick-preview--links)
4. [Inspiration](#inspiration)
5. [What It Does](#what-it-does)
6. [How We Built It](#how-we-built-it)
    - [Technology Stack](#technology-stack)
    - [User Workflow](#user-workflow)
    - [Rest APIs](#rest-apis)
    - [Database Schema](#database-schema)
7. [Challenges We Faced](#challenges-we-faced)
8. [Key Accomplishments](#key-accomplishments)
9. [Lessons Learned](#lessons-learned)
10. [What’s Next](#whats-next)

## Contributors

-   [Saurabh Zinjad](https://github.com/Ztrimus)
-   [Rohan Awhad](https://github.com/RohanAwhad)
-   [Harsh Challa](https://github.com/Harshchalla)
-   [Rajat Pawar](https://github.com/rajat98)

## Quick Preview & Links

-   [Try demo](https://peec.harora.lol/)
-   [Demo video](https://youtu.be/48cP6y--2Qg)
-   [User Documentation and Guide](https://github.com/2024-Arizona-Opportunity-Hack/HaRoRa-PajaritoEnvironmenta-FromMediaOverloadtoSeamlessOrganization/blob/main/User%20Documentation.pdf)
-   [DevPost project](https://devpost.com/software/image-search-and-tagging-tool)
-   [Presentation Deck](https://www.canva.com/design/DAGTelmxTQg/Zw9Lq4hmFJxN9nN0FUpgdQ/edit?utm_content=DAGTelmxTQg&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
-   [Team slack channel](https://opportunity-hack.slack.com/archives/C07RLQUHRR8)

## Inspiration

> Empowering NPOs with Accessible, Cost-Effective and Cloud-Based Technology

Our project was inspired by the unique challenges that nonprofit organizations (NPOs) face when managing large volumes of media files. While many cloud-based media management solutions exist, they tend to be costly and overly complex, making them inaccessible to smaller nonprofits or individuals with limited technical expertise. NPOs often have very niche use cases and require a solution tailored to their specific needs. By leveraging open-source models and AI, we aimed to create an affordable, easy-to-use media organization system that addresses these challenges.

## What It Does

Our system streamlines media management for nonprofits by automatically tagging and organizing images using AI. Users can upload media manually or through Dropbox, and easily search collections using content-based queries.
Our system uses AI models like CLIP, GPT-4 Mini, and Llama-3.1 to automatically tag and organize images based on visual content, descriptions, keywords and metadata, enabling users to easily search collections.

## How We Built It

-   **Frontend**: Built using React.js for an intuitive, interactive user interface.
-   **Backend**: Developed with FastAPI (Python) to handle API requests and facilitate communication between the front and backend.
-   **Cloud Infrastructure**: Hosted on AWS for reliable cloud storage and hosting.
-   **Database**: Postgres was selected for efficient data management and tagging.
-   **Dropbox Integration**: Implemented via the Dropbox API for seamless file handling.
-   **AI Functionality**: Integrated AI models, including:
    -   Embedding Generation: CLIP for generating image and text embeddings to enable automated tagging.
    -   Image Captioning: A prompt-driven approach for generating descriptive captions.
    -   Metadata Extraction: Extracting relevant metadata from images for better organization.

### Technology Stack

| Purpose  | Technologies        |
| -------- | ------------------- |
| Frontend | ReactJs(JavaScript) |
| Backend  | FastAPI(Python)     |
| Cloud    | AWS                 |
| Database | Postgres            |
| APIs     | Dropbox             |
| AI Model | Llama-3.1, CLIP     |

### User Workflow

![Image processing and retrieval system flowchart showing upload, AI analysis, and search operations.](https://raw.githubusercontent.com/2024-Arizona-Opportunity-Hack/HaRoRa-PajaritoEnvironmenta-FromMediaOverloadtoSeamlessOrganization/refs/heads/main/docs/resources/workflow.png)

### Rest APIs

![Rest APIs developed by team harora](https://raw.githubusercontent.com/2024-Arizona-Opportunity-Hack/HaRoRa-PajaritoEnvironmenta-FromMediaOverloadtoSeamlessOrganization/refs/heads/main/docs/resources/rest_apis.jpeg)

### Database Schema

<img src="https://raw.githubusercontent.com/2024-Arizona-Opportunity-Hack/HaRoRa-PajaritoEnvironmenta-FromMediaOverloadtoSeamlessOrganization/refs/heads/main/docs/resources/peec_db.png" alt="Database schema for image_detail table, including fields for URL, title, caption, tags, embedding vector, coordinates, timestamps, and metadata." width="50%">

## Challenges We Faced

-   **Dropbox Authentication**: Resolving issues with secure Dropbox authentication and API compatibility.
-   **Database Query Optimization**: Enhancing Postgres search query performance for fast and accurate media retrieval.
-   **Model Compatibility**: Identifying AI models with compatible embeddings for seamless integration and accurate tagging results.
-   **Frontend-Backend Integration**: Ensuring smooth communication between React.js and FastAPI.

## Key Accomplishments

-   **Significant Time Savings**: Achieved a 91.67% reduction in time spent on media management tasks, reducing average time per task from 2.00 hours to 0.17 hours.
-   **Cost Efficiency**: This substantial time reduction translated to an annual savings of approximately $2,383.33 in wages for the nonprofit organization, highlighting the financial benefits of implementing our system.
-   **AI-Driven Tagging**: Successfully integrated AI-driven tagging that automates the media organization process, significantly reducing manual effort and increasing accuracy in tagging.
-   **Customizable Tagging Options**: Implemented manual tagging features that allow users to add personalized tags to their files, providing flexibility and enhancing user experience by combining AI-generated tags with user-defined labels.
-   **User-Centric Design**: Prioritized a simple, intuitive interface to ensure accessibility for non-technical users, particularly benefiting nonprofit organizations with limited technical expertise.
-   **Achievement of Core Objectives**: Met critical project goals, including seamless integration of manual tagging, reliable cloud hosting, and effective Dropbox authentication, establishing a robust foundation for future enhancements.

## Lessons Learned

-   **Vector Search**: Mastered the implementation of vector-based search for improved media retrieval.
-   **Metadata Structuring**: Gained deeper insights into metadata organization for better media tagging and search efficiency.
-   **Dropbox Integration**: Overcame challenges related to secure API authorization for Dropbox.

## What’s Next

-   **Broader Cloud Integration**: We plan to extend support to other cloud services like Google Drive and OneDrive, offering more flexibility to users.
-   **Canva Integration**: We plan to integrate with PEEC's Canva account to streamline media editing and design processes directly from the media management platform.
-   **Digital Rights Management (DRM)**: Introducing metadata functionality for tracking image ownership and photo credits to ensure proper attribution and usage rights for each media file.
-   **Advanced Version Control**: Implementing version control for media files to track changes, prevent accidental overwrites, and allow restoration of previous file versions if needed.
-   **Storage Flexibility & Scalability**: Enhancing storage management tools and scalability to support growing media libraries, including the ability to archive files and track storage usage.
-   **Role-Based Access Control**: Setting up role-based permissions (e.g., admin vs. view-only) to allow secure file sharing and user access management.
-   **Mobile Accessibility**: Exploring mobile-friendly features to allow PEEC staff to manage and access their media library on the go.
