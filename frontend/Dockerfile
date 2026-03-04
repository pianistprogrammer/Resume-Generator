FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application (for production)
# RUN npm run build

# Expose port
EXPOSE 3000

# Development command (use npm run build && npm run preview for production)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
