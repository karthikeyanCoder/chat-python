# MongoDB Connection Troubleshooting Guide

## Issue: Network Timeout When Connecting to MongoDB Atlas

### Error Messages:
- `[WinError 10060] A connection attempt failed`
- `socket.gaierror: [Errno 11001] getaddrinfo failed`

## Solutions:

### 1. Check Your Internet Connection
```powershell
ping google.com
```

### 2. Verify MongoDB Atlas Cluster Status
- Login to MongoDB Atlas: https://cloud.mongodb.com
- Check if your cluster is running (not paused)
- If paused, click "Resume" or "Start"

### 3. Whitelist Your IP Address
In MongoDB Atlas:
1. Go to **Network Access** → **IP Access List**
2. Click **Add IP Address**
3. Choose **Add Current IP Address**
4. Or add `0.0.0.0/0` to allow all IPs (NOT recommended for production)

### 4. Check Firewall/Antivirus
Your Windows Firewall or Antivirus might be blocking the connection:
- Temporarily disable firewall to test
- Add an exception for Python in your antivirus

### 5. Try Alternative Connection String
Update your `.env` file with a connection string that includes retryWrites:
```
MONGO_URI=mongodb+srv://cloudservice:qIN55dvWcZEyRaE1@cluster0.zhrkdmn.mongodb.net/?retryWrites=true&w=majority&appName=YourApp
```

### 6. Test Connection Directly
Create a test script to verify connectivity

### 7. Check if Using a VPN/Proxy
If you're behind a corporate firewall or VPN, you may need to:
- Disconnect VPN temporarily
- Configure proxy settings
- Contact your network administrator

### 8. Alternative: Use Local MongoDB (Development)
For local development, you can install MongoDB locally:
```powershell
# Download from: https://www.mongodb.com/try/download/community
# Or use Docker:
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Then update `.env`:
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=patients_db
```

