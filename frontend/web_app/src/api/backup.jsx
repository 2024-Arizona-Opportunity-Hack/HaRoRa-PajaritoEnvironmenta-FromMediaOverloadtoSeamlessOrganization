/*import axios from 'axios';

// Set the base URL for Axios
axios.defaults.baseURL = 'http://localhost:5000'; // Update this to your backend URL

// Upload files to the server
export const uploadFiles = async (files, tags) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  formData.append('tags', tags);

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
  try {
    const response = await axios.put(`/tag/${uuid}`, { tags });
    return response.data;
  } catch (error) {
    console.error('Error updating tags:', error);
    throw error;
  }
};
*/
export const searchMedia = async (query) => {
    // Mock data
    const mockData = [
      {
        id: '1',
        filename: 'image1.jpg',
        thumbnailUrl: 'https://via.placeholder.com/300x200',
        tags: ['nature', 'forest'],
      },
      {
        id: '2',
        filename: 'image2.jpg',
        thumbnailUrl: 'https://via.placeholder.com/300x200',
        tags: ['city', 'buildings'],
      },
      {
        id: '3',
        filename: 'image3.jpg',
        thumbnailUrl: 'https://via.placeholder.com/300x200',
        tags: ['ocean', 'beach'],
      },
      // Add more items if needed
    ];
  
    // Simulate filtering based on the query
    const filteredData = mockData.filter((item) =>
      item.tags.some((tag) => tag.toLowerCase().includes(query.toLowerCase()))
    );
  
    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(filteredData);
      }, 500);
    });
  };