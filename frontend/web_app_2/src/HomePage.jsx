import React from 'react';
import { CheckIcon, SearchIcon, ImageIcon, FolderSync } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, description }) => (
  <div className="bg-white p-6 rounded-lg shadow-md transition-all duration-300 text-center">
    <div className="flex justify-center mb-4">
      <Icon className="w-12 h-12 text-blue-600" />
    </div>
    <h3 className="text-xl font-bold mb-3 text-gray-800">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

const HomePage = () => {
  return (
    <div className="min-h-screen font-inter">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 lg:py-24 max-w-6xl">
        <div className="grid md:grid-cols-2 gap-10 items-center font-grotesk">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-primary mb-6">
              PixQuery: Organize & Search Your Visuals
            </h1>
            <p className="text-xl text-secondary mb-8">
              Effortlessly Manage Your Dropbox Images with AI-Powered Intelligence
            </p>
            <button className="bg-blue-600 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-blue-700 transition-colors">
              Connect Dropbox
            </button>
          </div>
          <div className="hidden md:block">
            <div className="bg-white p-4 rounded-lg shadow-2xl">
              <img 
                src="/api/placeholder/600/400" 
                alt="PixQuery Interface" 
                className="rounded-md w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Powerful Features for Visual Management
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard 
              icon={ImageIcon}
              title="Auto Tagging & Categorization"
              description="Let AI do the work. PixQuery automatically tags your images, making them searchable by content, not just file names."
            />
            <FeatureCard 
              icon={SearchIcon}
              title="Custom Search Indexing"
              description="Specify which folders matter most. Create personalized search indexes for quick access to your most important visuals."
            />
            <FeatureCard 
              icon={FolderSync}
              title="Seamless Dropbox Sync"
              description="Keep your gallery up-to-date. PixQuery syncs with Dropbox to ensure your search index reflects the latest changes."
            />
            <FeatureCard 
              icon={CheckIcon}
              title="Canva Integration"
              description="Streamline your design workflow. Search for your Dropbox images right from Canva, perfect for marketing professionals."
            />
          </div>
        </div>
      </div>

      {/* Testimonial Section */}
      <div className="py-16">
        <div className="container mx-auto px-4 text-center">
          <blockquote className="max-w-2xl mx-auto text-xl italic text-gray-700 mb-6">
            "Since integrating PixQuery with our workflow, our team's efficiency in pulling assets for campaigns has skyrocketed!"
          </blockquote>
          <p className="font-semibold text-gray-800">- Jane Doe, Marketing Director</p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p>&copy; 2024 PixQuery. All rights reserved.</p>
          </div>
          <div className="flex space-x-4">
            <a href="/privacy" className="hover:text-blue-300">Privacy Policy</a>
            <a href="/terms" className="hover:text-blue-300">Terms of Service</a>
            <a href="mailto:contact@pixquery.com" className="hover:text-blue-300">Contact Us</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
