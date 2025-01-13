# Landline: Natural Language Interface for Geospatial Databases

~In development~

**Landline** is a simple yet powerful tool that allows anyone to interact with geospatial databases using natural language. Whether you're a map enthusiast, a researcher, or just curious about the world, Landline makes it easy to ask questions and see the answers visualized on a map.

### **How It Works**

1. **Ask a Question:** Type your query into the chatbox, like “Show me all the parks in Paris.”
2. **Get an Answer:** Landline’s intelligent engine translates your question into a database query and fetches the relevant data.
3. **Visualize It:** See the results instantly on an interactive map.

### **Why Use Landline?**

- **Simple:** No technical knowledge needed—just ask in plain language.
- **Interactive:** Explore the results directly on a map.
- **Efficient:** Access complex geospatial insights without writing code.

### **SSL Configuration**

The application is configured to use HTTPS with SSL certificates from Let's Encrypt. Here's what you need to know:

- **Certificate Location:** SSL certificates are stored in `/etc/letsencrypt/live/landline.world/`
- **Auto-Renewal:** Certificates auto-renew via Certbot's systemd timer
- **Security Features:**
  - Forced HTTPS redirection
  - TLS 1.2/1.3 only
  - Strong cipher suite configuration
  - HTTP Strict Transport Security (HSTS)

#### Setting up SSL on a New Server

1. Install Certbot:
   ```bash
   sudo apt update && sudo apt install -y certbot
   ```

2. Obtain certificate:
   ```bash
   sudo certbot certonly --standalone -d landline.world --email admin@landline.world --agree-tos
   ```

3. The Docker configuration automatically mounts the certificates and enables HTTPS.

Note: Ensure port 80 is free when running Certbot for initial certificate acquisition and renewals.

