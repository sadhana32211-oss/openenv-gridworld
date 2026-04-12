const express = require('express');
const app = express();

app.use(express.json());
const port = process.env.PORT || 7860;

app.use(express.json());
app.use(express.static('public'));

// ================= ENV =================
class GridWorldEnv {
  constructor(gridSize = 5, envId = 'default') {
    this.envId = envId;
    this.gridSize = gridSize;
    this.maxSteps = gridSize * gridSize * 4;

    this.rewards = {
      goal: 10,
      obstacle: -0.5,
      pit: -1,
      boundary: -0.1,
      step: -0.01
    };

    this.agentPos = { x: 0, y: 0 };
    this.goalPos = { x: gridSize - 1, y: gridSize - 1 };
    this.grid = [];
    this.steps = 0;
    this.totalReward = 0;
    this.done = false;

    this._init();
  }

  _init() {
    this.grid = [];

    for (let y = 0; y < this.gridSize; y++) {
      this.grid[y] = [];
      for (let x = 0; x < this.gridSize; x++) {
        this.grid[y][x] = 'empty';
      }
    }

    this.grid[0][0] = 'agent';
    this.grid[this.gridSize - 1][this.gridSize - 1] = 'goal';

    // obstacles + pits
    this.grid[1][2] = 'obstacle';
    this.grid[2][2] = 'obstacle';
    this.grid[3][2] = 'obstacle';
    this.grid[2][1] = 'pit';
    this.grid[2][3] = 'pit';
  }

  reset() {
    this.steps = 0;
    this.totalReward = 0;
    this.done = false;
    this.agentPos = { x: 0, y: 0 };
    this._init();
    return this.getState();
  }

  step(action) {
    const dx = [0, 1, 0, -1];
    const dy = [1, 0, -1, 0];

    let newX = this.agentPos.x + dx[action];
    let newY = this.agentPos.y + dy[action];

    let reward = -0.01;

    if (newX < 0 || newY < 0 || newX >= this.gridSize || newY >= this.gridSize) {
      reward = -0.1;
    } else {
      let cell = this.grid[newY][newX];

      if (cell === 'obstacle') reward = -0.5;
      else if (cell === 'pit') {
        reward = -1;
        this.done = true;
      } else if (cell === 'goal') {
        reward = 10;
        this.done = true;
      } else {
        this.grid[this.agentPos.y][this.agentPos.x] = 'empty';
        this.agentPos = { x: newX, y: newY };
        this.grid[newY][newX] = 'agent';
      }
    }

    this.steps++;
    this.totalReward += reward;

    return {
      state: this.getState(),
      reward,
      done: this.done,
      info: {}
    };
  }

  getState() {
    return {
      agent_position: this.agentPos,
      goal_position: this.goalPos,
      grid_size: this.gridSize,
      grid: this.grid,
      steps: this.steps,
      done: this.done,
      total_reward: this.totalReward
    };
  }

  getInfo() {
    return {
      name: "GridWorld-v0",
      grid_size: this.gridSize,
      action_space: {
        type: "discrete",
        n: 4,
        labels: ["UP", "RIGHT", "DOWN", "LEFT"]
      },
      observation_space: {
        type: "grid",
        shape: [this.gridSize, this.gridSize],
        cellTypes: ["empty", "agent", "goal", "obstacle", "pit"]
      },
      reward_range: { min: -1, max: 10 },
      max_steps: this.maxSteps,
      rewards: { ...this.rewards }
    };
  }
}

// ============ MANAGER ============
const envManager = new Map();

function getEnv(id = "default") {
  if (!envManager.has(id)) {
    envManager.set(id, new GridWorldEnv());
  }
  return envManager.get(id);
}

// ============ ROUTES ============

// ✅ REQUIRED FIX
app.post(['/reset', '/api/reset'], (req, res) => {
  const env = getEnv();
  const state = env.reset();

  res.json({
    env_id: "default",
    state,
    info: env.getInfo()
  });
});

// step
app.post(['/step', '/api/step'], (req, res) => {
  const action = parseInt(req.body.action || 0);
  const env = getEnv();

  const result = env.step(action);

  res.json({
    env_id: "default",
    ...result
  });
});
});

// state
app.get('/api/state', (req, res) => {
  const env = getEnv();

  res.json({
    env_id: "default",
    state: env.getState(),
    info: env.getInfo()
  });
});

// env info
app.get('/api/env/info', (req, res) => {
  const env = getEnv();
  res.json({
    name: "GridWorld-v0",
    description: "A classic grid world reinforcement learning environment where an agent navigates to reach a goal while avoiding obstacles and pits.",
    version: "1.0.0",
    ...env.getInfo()
  });
});

// list environments
app.get('/api/envs', (req, res) => {
  const envs = [];
  envManager.forEach((env, id) => {
    envs.push({
      env_id: id,
      ...env.getInfo(),
      current_state: env.getState()
    });
  });
  res.json({ environments: envs });
});

// delete environment
app.delete('/api/env/:env_id', (req, res) => {
  const { env_id } = req.params;
  if (envManager.has(env_id)) {
    envManager.delete(env_id);
    res.json({ success: true, message: `Environment '${env_id}' deleted` });
  } else {
    res.status(404).json({ success: false, message: `Environment '${env_id}' not found` });
  }
});

// Export the environment class and manager for use in other modules
module.exports = { GridWorldEnv, getEnv };

// Start server only if this is the main module
if (require.main === module) {
  app.listen(port, '0.0.0.0', () => {
    console.log("Server running on port " + port);
  });
}
