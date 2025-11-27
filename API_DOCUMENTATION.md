# CRM API Documentation

## Authentication

All API endpoints (except login) require authentication using token-based auth. Include the authorization header:

```
Authorization: Token YOUR_AUTH_TOKEN
```

## Base URL

```
http://localhost:8000/api
```

## Response Format

All responses are in JSON format. Success responses return `200 OK` or `201 Created` with data. Error responses return appropriate HTTP status codes with error details.

---

## Leads Endpoints

### 1. List All Leads

**GET** `/leads/`

Query Parameters:
- `search` - Search by name or phone
- `status` - Filter by status (new, contacted, qualified, converted, lost)
- `source` - Filter by source (google_sheets, excel_upload, csv_upload, manual)
- `page` - Page number (default: 1)

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/leads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "phone": "+1234567890",
      "source": "manual",
      "status": "new",
      "assigned_to": 2,
      "assigned_to_username": "salesperson1",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 2. Create Lead

**POST** `/leads/`

**Request Body:**
```json
{
  "name": "Jane Smith",
  "phone": "+1987654321",
  "source": "manual",
  "status": "new",
  "assigned_to": null
}
```

**Response:** `201 Created`
```json
{
  "id": 101,
  "name": "Jane Smith",
  "phone": "+1987654321",
  "source": "manual",
  "status": "new",
  "assigned_to": null,
  "assigned_to_username": null,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### 3. Get Lead Details

**GET** `/leads/{id}/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "+1234567890",
  "source": "manual",
  "status": "new",
  "assigned_to": 2,
  "assigned_to_username": "salesperson1",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Update Lead

**PUT** `/leads/{id}/`

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "phone": "+1234567890",
  "source": "manual",
  "status": "contacted",
  "assigned_to": 2
}
```

**Response:** `200 OK` with updated lead data

### 5. Partial Update Lead

**PATCH** `/leads/{id}/`

**Request Body:** (only fields to update)
```json
{
  "status": "qualified",
  "assigned_to": 3
}
```

### 6. Delete Lead

**DELETE** `/leads/{id}/`

**Response:** `204 No Content`

### 7. Get Leads by Status

**GET** `/leads/by_status/?status=new`

**Response:** `200 OK` - List of leads with specified status

### 8. Get Leads by Salesperson

**GET** `/leads/by_salesperson/?salesperson_id=2`

**Response:** `200 OK` - List of leads assigned to specified salesperson

### 9. Mark Lead as Contacted

**POST** `/leads/{id}/mark_contacted/`

**Response:** `200 OK`
```json
{
  "status": "Lead marked as contacted"
}
```

### 10. Assign Lead to Salesperson

**POST** `/leads/{id}/assign_to_salesperson/`

**Request Body:**
```json
{
  "salesperson_id": 3
}
```

**Response:** `200 OK` with updated lead data

---

## Import Endpoints

### 1. Upload Excel File

**POST** `/imports/upload-excel/`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` - Excel file (.xlsx)

**Response:** `202 Accepted`
```json
{
  "status": "File uploaded and import started",
  "file_name": "leads.xlsx"
}
```

### 2. Upload CSV File

**POST** `/imports/upload-csv/`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` - CSV file (.csv)

**Response:** `202 Accepted`
```json
{
  "status": "File uploaded and import started",
  "file_name": "leads.csv"
}
```

### 3. Get Import Status

**GET** `/imports/status/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "import_type": "Excel",
    "status": "completed",
    "total_records": 50,
    "imported_count": 48,
    "duplicate_count": 2,
    "error_count": 0,
    "file_name": "leads.xlsx",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:02:30Z"
  }
]
```

---

## Reminders Endpoints

### 1. Get Pending Reminders

**GET** `/reminders/pending_reminders/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "lead": 1,
    "lead_name": "John Doe",
    "lead_phone": "+1234567890",
    "assigned_to_username": "salesperson1",
    "status": "pending",
    "contact_deadline": "2024-01-15T10:35:00Z",
    "last_reminder_at": null,
    "contacted_at": null,
    "reminder_count": 0
  }
]
```

### 2. Get Overdue Reminders

**GET** `/reminders/overdue_reminders/`

**Response:** `200 OK` - List of reminders past deadline

### 3. Get All Reminders

**GET** `/reminders/`

**Query Parameters:**
- `status` - Filter by status (pending, notified, contacted, snoozed)
- `page` - Page number

### 4. Mark Reminder as Contacted

**POST** `/reminders/{id}/mark_contacted/`

**Response:** `200 OK`
```json
{
  "status": "Reminder marked as contacted"
}
```

### 5. Snooze Reminder

**POST** `/reminders/{id}/snooze/`

**Request Body:**
```json
{
  "snooze_minutes": 15
}
```

**Response:** `200 OK`
```json
{
  "status": "Reminder snoozed for 15 minutes"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "details": "Phone number must be at least 10 digits."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 409 Conflict
```json
{
  "error": "Lead with this phone already exists"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error",
  "message": "Error details..."
}
```

---

## Import File Format

### Excel Format (.xlsx)

| Name | Phone |
|------|-------|
| John Doe | +1234567890 |
| Jane Smith | +1987654321 |
| Bob Johnson | +1122334455 |

### CSV Format (.csv)

```
Name,Phone
John Doe,+1234567890
Jane Smith,+1987654321
Bob Johnson,+1122334455
```

---

## Rate Limiting

Currently no rate limiting is implemented. Implement in production.

## Pagination

Default page size: 20 items per page

**Example:**
```
GET /leads/?page=2
```

## Filtering & Search

**Search across name and phone:**
```
GET /leads/?search=john
```

**Filter by multiple criteria:**
```
GET /leads/?status=new&source=google_sheets
```

---

## WebSocket Events (Optional Enhancement)

Future versions will support WebSocket for real-time updates:
- `lead_created` - New lead added
- `import_completed` - Import process finished
- `reminder_triggered` - Reminder deadline reached

---

## Example Requests

### Using cURL

**Get all leads:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/leads/
```

**Create a lead:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","phone":"+1234567890","source":"manual","status":"new"}' \
  http://localhost:8000/api/leads/
```

**Upload Excel file:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@leads.xlsx" \
  http://localhost:8000/api/imports/upload-excel/
```

### Using JavaScript/Fetch

**Get leads:**
```javascript
const response = await fetch('http://localhost:8000/api/leads/', {
  headers: {
    'Authorization': 'Token YOUR_TOKEN'
  }
});
const data = await response.json();
console.log(data);
```

**Upload file:**
```javascript
const formData = new FormData();
formData.append('file', file);

const response = await fetch('http://localhost:8000/api/imports/upload-excel/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token YOUR_TOKEN'
  },
  body: formData
});
const result = await response.json();
console.log(result);
```

---

## Best Practices

1. **Always validate input data** before sending to API
2. **Handle errors gracefully** on the client side
3. **Implement proper error messages** for users
4. **Use HTTPS** in production
5. **Keep tokens secure** and never expose in client-side code
6. **Cache responses** when appropriate
7. **Implement request timeouts** to prevent hanging requests
8. **Log API errors** for debugging

---

## Support

For API issues and questions, contact: api-support@educationcrm.com
