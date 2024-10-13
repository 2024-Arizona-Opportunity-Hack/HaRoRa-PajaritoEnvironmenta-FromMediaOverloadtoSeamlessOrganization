

# **Web App**

This project is a media management web application built using **React**, **Vite**, **Axios**, **Tailwind CSS**, **DaisyUI**, and **FastAPI** for backend integration (specifically with Dropbox for file management). The application allows users to upload files, manage tags, and search media items based on metadata.

---

## **Features**

- **File Upload**: Users can upload media files and add associated tags. Uploaded files are stored in the cloud (e.g., Dropbox) using an OAuth authentication flow.
- **Tag Management**: Users can manually edit or update tags for each media item, with the option for bulk tagging.
- **Search Functionality**: Users can search for media items based on tags, filenames, or other metadata and view thumbnails of the media files in a responsive grid layout.
- **Protected Routes**: Specific pages are protected and require login via Dropbox OAuth authentication to access.

---

## **Project Structure**

```bash
.
├── public/                 # Public assets served directly
├── src/                    # Main source code folder
│   ├── api/                # API interaction functions
│   │   ├── api.jsx         # Core API calls (upload, search, tag management)
│   │   └── backup.jsx      # Backup-specific API functions
│   ├── components/         # Reusable UI components
│   │   ├── Navbar.jsx      # Navigation bar for the application
│   │   ├── Search.jsx      # Search component for media items
│   │   ├── TagEditor.jsx   # Tag editor component for media items
│   │   └── Upload.jsx      # Upload component for drag-and-drop file uploads
│   ├── pages/              # Individual pages
│   │   ├── SearchPage.jsx  # Search page layout
│   │   └── UploadPage.jsx  # Upload page layout
│   ├── assets/             # Static assets (SVGs, images, etc.)
│   ├── App.jsx             # Main app entry point
│   ├── main.jsx            # React application entry point
│   ├── App.css             # App-level global styles
│   └── index.css           # Tailwind and DaisyUI styles
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.js          # Vite configuration
├── postcss.config.js       # PostCSS configuration
├── package.json            # Project metadata and dependencies
└── README.md               # Project documentation
```

---

## **Installation**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/media-management-app.git
   cd media-management-app
   ```

2. **Install Dependencies**:

   Ensure you have Node.js installed, then run:

   ```bash
   npm install
   ```

3. **Configure Environment Variables**:

   For Dropbox OAuth and FastAPI integration, ensure you have the following environment variables set up in your backend environment:

   - `DROPBOX_CLIENT_ID`
   - `DROPBOX_CLIENT_SECRET`
   - `FASTAPI_SESSION_SECRET_KEY`

4. **Run the Application**:

   You can run the React application locally using Vite:

   ```bash
   npm run dev
   ```

   This will start the app at `http://localhost:5173`.

5. **Backend Server (FastAPI)**:

   If you are using FastAPI for the backend, ensure the backend server is running by following its specific instructions:

   ```bash
   uvicorn backend:app --reload --port 8080
   ```

   This will start the backend at `http://localhost:8080`.

---

## **Usage**

### **Authentication**

The application uses Dropbox OAuth for user authentication. When you attempt to upload files or access protected routes, you will be prompted to log in to Dropbox. After successful login, you can upload media files, manage their tags, and search for media items.

### **Uploading Files**

1. Navigate to the **Upload Page** (`/upload`).
2. Drag and drop files into the designated area or select files manually.
3. Add relevant tags for the files.
4. Click **Upload** to upload the files to Dropbox.

### **Searching for Media**

1. Navigate to the **Search Page** (`/search`).
2. Use the search bar to enter keywords (tags, filenames).
3. View the media items in a 3x3 grid layout, showing thumbnails, metadata, and tags.

### **Tag Management**

- Each media item includes an **Edit Tags** button.
- Click the button to modify or update the tags for that media item.
- Save the changes, and the updated tags will be reflected immediately.

### **Protected Pages**

Some pages, like the **Search Page** and **Upload Page**, require the user to be logged in via Dropbox OAuth. Users who are not logged in will see a message prompting them to authenticate.

---

## **Development Workflow**

1. **Building the Project**:
   To create an optimized production build:

   ```bash
   npm run build
   ```

2. **Linting and Code Style**:
   The project uses ESLint for maintaining code quality and consistency. You can run the linter with:

   ```bash
   npm run lint
   ```

---

## **API Documentation**

This project uses Axios to communicate with the backend API. Below is an overview of the API functions provided in the `api.jsx` file:

- **`uploadFiles(files, tags)`**: Uploads media files along with associated tags.
- **`searchMedia(query)`**: Searches for media files based on tags or metadata.
- **`getTags(uuid)`**: Fetches the tags associated with a media item.
- **`updateTags(uuid, tags)`**: Updates the tags for a specific media item.

For more information, see the comments in `src/api/api.jsx`.

---

## **Styling and UI**

- **Tailwind CSS**: Provides utility-first styling for rapid UI development.
- **DaisyUI**: Enhances the Tailwind framework with pre-designed components, such as buttons, modals, and cards.
- **Responsive Design**: The app is fully responsive, with key components (like the upload area and media grid) optimized for different screen sizes.

---





