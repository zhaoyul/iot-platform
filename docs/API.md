# API Documentation

## Overview

The IoT Platform provides a comprehensive REST API for managing Git repositories, industrial assets, and visualizations.

## Base URLs

- **Git Parser API**: `http://localhost:8080/api/v1`
- **Asset Manager API**: `http://localhost:8082/api/v1`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Git Parser API

### Get Commit Information

Retrieve detailed information about a specific commit.

**Endpoint:** `GET /repos/{repo}/commits/{commit}`

**Parameters:**
- `repo` (path) - Repository name
- `commit` (path) - Commit hash

**Response:**
```json
{
  "hash": "abc123...",
  "message": "Add new feature",
  "author": "John Doe",
  "email": "john@example.com",
  "date": "2024-12-18T10:00:00Z",
  "file_count": 15
}
```

**Example:**
```bash
curl http://localhost:8080/api/v1/repos/my-project/commits/abc123
```

### Analyze Diff

Compare two commits and get detailed diff analysis.

**Endpoint:** `GET /repos/{repo}/diff`

**Query Parameters:**
- `from` - Starting commit hash
- `to` - Ending commit hash

**Response:**
```json
{
  "files_changed": 5,
  "additions": 150,
  "deletions": 75,
  "files": [
    "src/main.py",
    "src/utils.py",
    "README.md"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8080/api/v1/repos/my-project/diff?from=abc123&to=def456"
```

### Get Repository Dependencies

Analyze repository dependencies and generate a dependency graph.

**Endpoint:** `GET /repos/{repo}/dependencies`

**Query Parameters:**
- `branch` (optional) - Branch name (default: main)
- `depth` (optional) - Analysis depth (default: 10)

**Response:**
```json
{
  "modules": [
    {
      "id": "1",
      "name": "core",
      "type": "module",
      "dependencies": [],
      "metrics": {
        "lines": 1500,
        "complexity": 25
      }
    }
  ],
  "dependencies": [
    {
      "from": "ui",
      "to": "core",
      "type": "import"
    }
  ]
}
```

## Asset Manager API

### Upload Asset

Upload a new asset file to the platform.

**Endpoint:** `POST /assets/upload`

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `file` - The file to upload
- `asset_type` - Type of asset (code, binary, plc, eda, firmware, config)
- `repository` - Repository name
- `branch` - Branch name

**Response:**
```json
{
  "status": "success",
  "asset": {
    "id": "abc123",
    "name": "motor_control.st",
    "type": "plc",
    "size": 2048,
    "hash": "sha256:...",
    "repository": "plc-programs",
    "branch": "main",
    "created_at": "2024-12-18T10:00:00Z"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8082/api/v1/assets/upload \
  -F "file=@motor_control.st" \
  -F "asset_type=plc" \
  -F "repository=plc-programs" \
  -F "branch=main"
```

### Get Asset

Retrieve information about a specific asset.

**Endpoint:** `GET /assets/{asset_id}`

**Response:**
```json
{
  "id": "abc123",
  "name": "motor_control.st",
  "type": "plc",
  "size": 2048,
  "hash": "sha256:...",
  "repository": "plc-programs",
  "metadata": {
    "language": "ST",
    "version": "1.0"
  }
}
```

### List Assets

List all assets with optional filtering.

**Endpoint:** `GET /assets`

**Query Parameters:**
- `asset_type` (optional) - Filter by asset type
- `repository` (optional) - Filter by repository
- `limit` (optional) - Results per page (default: 50)
- `offset` (optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "total": 150,
  "items": [
    {
      "id": "abc123",
      "name": "motor_control.st",
      "type": "plc",
      "size": 2048
    }
  ],
  "limit": 50,
  "offset": 0
}
```

### Parse PLC Program

Parse and analyze a PLC program.

**Endpoint:** `POST /plc/parse`

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `file` - PLC program file

**Response:**
```json
{
  "id": "abc123",
  "name": "motor_control.st",
  "language": "ST",
  "variables": [
    {
      "name": "StartButton",
      "type": "BOOL",
      "scope": "VAR"
    }
  ],
  "function_blocks": [],
  "programs": [
    {
      "name": "MotorControl",
      "type": "PROGRAM"
    }
  ]
}
```

### Parse EDA Design

Parse and analyze an EDA design file.

**Endpoint:** `POST /eda/parse`

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `file` - EDA design file

**Response:**
```json
{
  "id": "abc123",
  "name": "board.kicad_pcb",
  "tool": "KiCad",
  "components": [
    {
      "reference": "R1",
      "value": "10K",
      "footprint": "Resistor_SMD:R_0805"
    }
  ],
  "nets": [
    {
      "name": "GND",
      "nodes": 50
    }
  ],
  "layers": 2,
  "board_size": {
    "width": 100.0,
    "height": 80.0
  }
}
```

## Webhook Events

The platform supports webhooks for real-time notifications.

### Available Events

- `repository.create` - New repository created
- `repository.push` - Code pushed to repository
- `asset.upload` - New asset uploaded
- `asset.delete` - Asset deleted
- `plc.validate` - PLC program validated
- `eda.validate` - EDA design validated

### Webhook Payload

```json
{
  "event": "repository.push",
  "timestamp": "2024-12-18T10:00:00Z",
  "repository": "my-project",
  "branch": "main",
  "commits": [
    {
      "hash": "abc123",
      "message": "Update README",
      "author": "John Doe"
    }
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid file format",
    "details": {
      "field": "file",
      "reason": "Unsupported file type"
    }
  }
}
```

### Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 60 requests per hour

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1640000000
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

```
GET /api/v1/assets?limit=20&offset=40
```

Response includes pagination metadata:

```json
{
  "total": 150,
  "items": [...],
  "limit": 20,
  "offset": 40,
  "has_more": true
}
```

## SDK Examples

### Python

```python
import requests

# Get commit info
response = requests.get(
    'http://localhost:8080/api/v1/repos/my-project/commits/abc123',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
commit = response.json()
print(f"Commit by {commit['author']}: {commit['message']}")

# Upload asset
with open('motor_control.st', 'rb') as f:
    response = requests.post(
        'http://localhost:8082/api/v1/assets/upload',
        files={'file': f},
        data={
            'asset_type': 'plc',
            'repository': 'plc-programs',
            'branch': 'main'
        }
    )
print(response.json())
```

### JavaScript

```javascript
// Get commit info
const response = await fetch(
  'http://localhost:8080/api/v1/repos/my-project/commits/abc123',
  {
    headers: {
      'Authorization': 'Bearer YOUR_TOKEN'
    }
  }
);
const commit = await response.json();
console.log(`Commit by ${commit.author}: ${commit.message}`);

// Upload asset
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('asset_type', 'plc');
formData.append('repository', 'plc-programs');
formData.append('branch', 'main');

const uploadResponse = await fetch(
  'http://localhost:8082/api/v1/assets/upload',
  {
    method: 'POST',
    body: formData
  }
);
console.log(await uploadResponse.json());
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func getCommitInfo(repo, commit string) {
    url := fmt.Sprintf("http://localhost:8080/api/v1/repos/%s/commits/%s", repo, commit)
    
    req, _ := http.NewRequest("GET", url, nil)
    req.Header.Set("Authorization", "Bearer YOUR_TOKEN")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Printf("Commit: %v\n", result)
}

func uploadAsset(filename string) {
    file, _ := os.Open(filename)
    defer file.Close()
    
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    
    part, _ := writer.CreateFormFile("file", filename)
    io.Copy(part, file)
    
    writer.WriteField("asset_type", "plc")
    writer.WriteField("repository", "plc-programs")
    writer.WriteField("branch", "main")
    writer.Close()
    
    req, _ := http.NewRequest("POST", "http://localhost:8082/api/v1/assets/upload", body)
    req.Header.Set("Content-Type", writer.FormDataContentType())
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Printf("Upload result: %v\n", result)
}
```

## Support

For API support and questions:
- GitHub Issues: https://github.com/zhaoyul/iot-platform/issues
- Documentation: https://docs.iot-platform.com
