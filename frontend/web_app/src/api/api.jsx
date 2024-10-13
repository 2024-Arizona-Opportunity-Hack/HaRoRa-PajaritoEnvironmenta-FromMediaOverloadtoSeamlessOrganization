import axios from 'axios';

// Set the base URL for Axios
axios.defaults.baseURL = 'http://localhost:8080'; // Update this to your backend URL

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

// Search for media (mocked for testing)
export const searchMedia = async (query) => {
  // Mock data structure based on your example
return{
    results: [
      {
        url: "/tmp/79aba3e1-60af-4145-893e-598407ec3f62.jpeg",
        title: "A student wearing headphones and working on a laptop in a classroom setting",
        caption: "A young man with dark hair, wearing white pants and a black shirt, sits in a beige chair at a desk with a laptop and tablet. He is wearing headphones and has a backpack on the floor next to him.",
        tags: "student,headphones,laptop,tablet,classroom,desk,backpack,beige,white,black,dark hair,young man",
        uuid: "1121a4c1-9bbd-4d86-91b7-4a34498fb5ac",
      },
    ],
  };

  // Simulating an API delay
  return new Promise((resolve) => {
    setTimeout(() => {
      // Filter mock data by query if provided
      const filteredResults = mockData.results.filter((item) =>
        item.title.toLowerCase().includes(query.toLowerCase())
      );
      resolve({ results: filteredResults });
    }, 500); // Simulated delay of 500ms
  });
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
