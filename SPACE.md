# 🌍 OpenEnv GridWorld - Hugging Face Space

This is the Hugging Face Space version of the OpenEnv GridWorld environment.

## 🚀 Quick Start

The Space is automatically deployed and ready to use at:
**https://huggingface.co/spaces/YOUR_USERNAME/openenv-gridworld**

## 📁 Project Structure

```
openenv-project/
├── index.js          # Node.js Express server with GridWorldEnv
├── agent.js          # Q-Learning agent implementation
├── inference.py      # Hugging Face inference script (required)
├── app.py           # Hugging Face Space entry point
├── requirements.txt  # Python dependencies
├── package.json      # Node.js dependencies
├── README.md         # Main project documentation
├── SPACE.md          # This file (Hugging Face Space docs)
└── public/           # Web interface files
    ├── index.html    # Main interactive interface
    ├── home.html     # Home page
    ├── about.html    # About page
    └── css/
        └── style.css # Styles
```

## 🔧 Technical Details

This Space uses a hybrid architecture:

1. **Node.js Backend**: Serves the GridWorld environment API
2. **FastAPI Proxy**: Handles requests and proxies to Node.js
3. **Static Web Interface**: Interactive HTML/CSS/JavaScript frontend

## 📋 Required Files for Hugging Face Spaces

- ✅ `inference.py` - Required by Hugging Face for inference
- ✅ `app.py` - Main application entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `public/` - Static web files

## 🎮 How to Use

1. **Visit the Space**: Go to your Space URL
2. **Interactive Grid**: Use WASD or arrow keys to control the agent
3. **API Access**: Use the REST API endpoints for programmatic access
4. **Agent Training**: Run the Q-Learning demo from the agent.js file

## 📡 API Endpoints

All standard OpenEnv API endpoints are available:

- `POST /api/reset` - Reset environment
- `POST /api/step` - Take an action (0-3)
- `GET /api/state` - Get current state
- `GET /api/env/info` - Get environment info
- `GET /api/envs` - List environments
- `DELETE /api/env/:env_id` - Delete environment

## 🤖 Q-Learning Agent

The project includes a complete Q-Learning implementation that can be trained to solve the GridWorld environment. See `agent.js` for the implementation.

## 🌐 Web Interface

The interactive web interface provides:
- Real-time grid visualization
- Keyboard controls (WASD/arrow keys)
- Environment information display
- Action buttons
- Reward tracking

## 📦 Dependencies

### Python (Hugging Face)
- FastAPI - Web framework
- Uvicorn - ASGI server
- Requests - HTTP client

### Node.js (Backend)
- Express - Web framework
- Static file serving

## 🚀 Deployment

To deploy to Hugging Face Spaces:

1. Create a new Space at https://huggingface.co/spaces
2. Choose "Docker" or "Static" SDK
3. Push your code to the Space repository
4. The Space will automatically build and deploy

## 🐛 Troubleshooting

### Node.js Server Issues
If the Node.js server fails to start:
- Check that `index.js` is present
- Verify Node.js is installed in the Space environment
- Check the Space logs for error messages

### Python Dependencies
If Python dependencies are missing:
- Ensure `requirements.txt` is present
- Check that all packages are compatible with the Space environment

## 📄 License

ISC License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions:
- Create an issue on the GitHub repository
- Check the Space documentation
- Review the API documentation in the web interface