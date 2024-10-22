import axios from 'axios';

// Set the base URL for Axios
//axios.defaults.baseURL = process.env.WEBPAGE_URL + '/api/v1'; // Use environment variable for backend URL
axios.defaults.baseURL = 'http://localhost/api'; // Use environment variable for backend URL

// Auth
// get profile info
export const getProfileInfo = async () => {
    try {
        const response = await axios.get('/profile');
        return { response: response.data, err: null };
    } catch (error) {
        console.log(error);
        if (error.response && error.response.status === 401) {
            return { response: null, err: 'Please login with Dropbox' };
        } else {
            return { response: null, err: 'Error: ' + error.message };
        }
    }
};

// login
export const handleLogin = async () => {
    try {
        const response = await axios.get('/login');
        const authUrl = response.data.auth_url;
        window.location.href = authUrl;
    } catch (error) {
        console.error('Error:', error);
    }
};

//logout
export const handleLogout = async (setProfile, setError) => {
    axios
        .get('/logout')
        .then((response) => {
            setProfile(null);
            setError(null);
        })
        .catch((error) => {
            console.log(error);
            setError('Error: ' + error.message);
        });
};

// Upload files to the server
export const uploadFiles = async (files, tags) => {
    const formData = new FormData();

    files.forEach((file) => formData.append('files', file));
    formData.append('tags', tags);
    console.log(files.length);

    try {
        const response = await axios.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading files:', error);
        throw error;
    }
};

// Search for media
export const searchMedia = async (query) => {
    try {
        const response = await axios.get('/search', { params: { q: query } });
        return response.data;
    } catch (error) {
        console.error('Error searching media:', error);
        throw error;
    }
};

// Get or update tags for a specific media item
export const getTags = async (uuid) => {
    try {
        const response = await axios.get(`/tag/${uuid}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching tags:', error);
        throw error;
    }
};

export const updateTags = async (uuid, tags) => {
    let data = JSON.stringify(tags);
    let config = {
        method: 'put',
        maxBodyLength: Infinity,
        url: `/tag/${uuid}`,
        headers: {
            accept: 'application/json',
            'Content-Type': 'application/json',
        },
        data: data,
    };

    axios
        .request(config)
        .then((response) => {
            console.log(JSON.stringify(response.data));
        })
        .catch((error) => {
            console.log(error);
        });
};
