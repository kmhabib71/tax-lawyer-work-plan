# RAGFlow Startup Instructions for Week 1 Completion

## Prerequisites
- Docker Desktop installed on Windows 11
- 8GB RAM (optimized configuration provided)
- Core i3 processor

## Step 1: Start RAGFlow Server

### Using Windows PowerShell (as Administrator):

```powershell
# Navigate to RAGFlow directory
cd "D:\Projects\Ai_TAX_LAWER_BANGLADESH\data-scrap\ragflow"

# Verify .env file exists (already created)
ls .env

# Start RAGFlow with slim configuration
docker-compose up -d

# Check if services are running
docker-compose ps

# Check logs if needed
docker-compose logs ragflow
```

### Expected Output:
```
✅ ragflow-server    running
✅ mysql            running  
✅ redis            running
```

## Step 2: Verify RAGFlow is Accessible

Open browser and go to: `http://localhost:9380`

You should see RAGFlow interface.

## Step 3: Create Knowledge Base (via API or UI)

Once RAGFlow is running, proceed with knowledge base creation.

## Troubleshooting

### If RAGFlow fails to start:
1. Check Docker Desktop is running
2. Ensure ports 9380, 3306, 6379 are free
3. Check .env configuration
4. Try: `docker-compose down && docker-compose up -d`

### Memory Issues (8GB RAM):
- The .env file is already optimized for 8GB RAM
- Close other applications if needed
- Monitor with: `docker stats`

## Next Steps After RAGFlow Starts:
1. Run: `python ragflow_client.py` to test connection
2. Upload legal documents to knowledge base
3. Test search and chat functionality
4. Complete Week 1 validation