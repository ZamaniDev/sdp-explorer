# Technician-Site Matrix Manager

## Overview

A modern, visual tool for managing technician-site associations in ManageEngine Service Desk Plus. This tool provides a spreadsheet-like interface where admins can quickly view and modify which sites each technician has access to.

## Problem Solved

**Before:** Admins had to:
- Navigate to each technician's profile individually
- Manually add/remove sites one at a time
- No overview of all technician-site relationships
- Time-consuming for bulk changes
- Difficult to audit site access

**After:** Admins can:
- See all technician-site relationships at a glance
- Toggle site access with checkboxes
- Make bulk changes across multiple technicians
- Search and filter technicians
- Track pending changes before saving
- Save individual or bulk updates

## Features

### 1. **Matrix View**
- Rows: Technicians (with name, email, department, status)
- Columns: Sites (with full site names)
- Checkboxes: Quick toggle for associations
- Sticky columns: Technician info and actions always visible

### 2. **Real-time Modification Tracking**
- Yellow highlighting for modified rows
- Live counter of pending changes
- Changes summary panel
- Individual or bulk save options

### 3. **Search & Filters**
- Search technicians by name or email
- Filter by status (All, Active Only, Modified Only)
- Real-time filtering

### 4. **Smart Save Operations**
- Save individual technician (per row)
- Save all changes (bulk update)
- Cancel all changes (reset to original)
- Optimistic UI updates

### 5. **User Experience**
- Modern, clean interface
- Loading indicators
- Success/error notifications
- Responsive design
- Sticky headers for scrolling

## How It Works

### Technical Flow

1. **GET Current State**
   ```
   GET /technicians -> List all technicians
   GET /technicians/{id} -> Get current associated_sites
   ```

2. **User Makes Changes**
   - Click checkboxes to add/remove site associations
   - Changes tracked in memory (not saved yet)
   - Visual feedback shows modified state

3. **PUT Updated State**
   ```json
   PUT /technicians/{id}
   {
     "technician": {
       "associated_sites": [
         {"id": "1508"},
         {"id": "4510"},
         {"id": "5402"}
       ]
     }
   }
   ```

### API Endpoints Used

**Backend Routes:**
- `GET /tools/site-matrix` - Render the tool page
- `GET /api/tools/site-matrix/data` - Get all technicians and sites
- `GET /api/tools/site-matrix/technician/{id}` - Get specific technician details
- `PUT /api/tools/site-matrix/update` - Update single technician's sites
- `PUT /api/tools/site-matrix/bulk-update` - Update multiple technicians

**ME SDP API:**
- `GET /technicians` - List all technicians
- `GET /technicians/{id}` - Get technician details
- `PUT /technicians/{id}` - Update technician
- `GET /sites` or `GET /accounts` - List all sites

## Usage

### Access the Tool

1. **Login** to SDP Explorer
2. **Click** "Site Matrix" in the navigation bar
3. **Wait** for data to load (shows technicians and sites)

### Make Changes

1. **Find technician** using search or scroll
2. **Click checkboxes** to toggle site associations
   - Checked = Technician has access to site
   - Unchecked = No access
3. **Row turns yellow** to indicate pending changes

### Save Changes

**Option 1: Save Individual Row**
- Click "Save" button on the modified row
- Saves only that technician's changes

**Option 2: Save All Changes**
- Click "Save All Changes" button at top
- Saves all modified technicians in bulk
- Confirmation dialog shows summary

### Cancel Changes

- Click "Cancel All" in pending changes panel
- Resets all modifications
- Returns to original state

## Permissions Required

**Admin API Key Required** for:
- Updating technician site associations
- PUT requests to `/technicians/{id}`

**Technician API Key** works for:
- Viewing the matrix (read-only essentially)
- Cannot save changes without admin key

## UI Guide

### Header Section
```
┌─────────────────────────────────────────────┐
│ Technician-Site Matrix        [Search]     │
│                               [Save All]    │
│                               [Refresh]     │
└─────────────────────────────────────────────┘
```

### Stats Section
```
┌─────────────────────────────────────────────┐
│ Technicians: 45  Sites: 23  Modified: 3    │
└─────────────────────────────────────────────┘
```

### Matrix Table
```
┌────────────────┬───┬───┬───┬───┬─────────┐
│ Technician     │ S1│ S2│ S3│ S4│ Actions │
├────────────────┼───┼───┼───┼───┼─────────┤
│ John Doe       │ ☑ │ ☐ │ ☑ │ ☐ │ [Save]  │
│ tech@email.com │   │   │   │   │         │
├────────────────┼───┼───┼───┼───┼─────────┤
│ Jane Smith     │ ☐ │ ☑ │ ☑ │ ☑ │ [Save]  │
│ jane@email.com │   │   │   │   │         │
└────────────────┴───┴───┴───┴───┴─────────┘
```

## Best Practices

### 1. **Review Before Saving**
- Check the "Pending Changes" summary
- Verify site counts (X → Y sites)
- Use individual saves for critical changes

### 2. **Test with One Technician First**
- Make change for one tech
- Save and verify in SDP
- Then proceed with bulk changes

### 3. **Use Filters**
- "Active Only" to hide inactive technicians
- "Modified Only" to see pending changes
- Search to find specific technicians

### 4. **Regular Audits**
- Review matrix monthly
- Check for technicians with too many/few sites
- Ensure proper access control

## Troubleshooting

### Issue: "No API credential configured"
**Solution:** Add admin API key in your Profile page

### Issue: "Failed to save"
**Solution:**
- Check your API key has admin permissions
- Verify technician ID exists
- Check site IDs are valid

### Issue: Data not loading
**Solution:**
- Click "Refresh" button
- Check browser console for errors
- Verify API connectivity

### Issue: Changes not visible after save
**Solution:**
- Click "Refresh" to reload data
- Check if save actually succeeded
- Verify in SDP admin panel

## Technical Details

### Frontend (site_matrix.html)
- Pure JavaScript (no framework)
- AJAX for API calls
- In-memory state management
- Optimistic UI updates
- Responsive table with sticky columns

### Backend (site_matrix_routes.py)
- Flask routes for API
- Permission checking
- Error handling
- Bulk operation support

### State Management
```javascript
matrixData = {
    technicians: [],        // All technicians
    sites: [],             // All sites
    originalState: {},     // Original site associations
    modifiedState: {}      // Modified associations
}
```

### Save Logic
1. Compare `modifiedState` vs `originalState`
2. Only send modified technicians to API
3. Build `associated_sites` array from site IDs
4. PUT to ME SDP API
5. Update `originalState` on success
6. Clear `modifiedState`
7. Update UI

## Integration with SDP Ecosystem

This tool is the **first productivity tool** in the SDP Enhancement Ecosystem strategy:

**Current Tool:** Technician-Site Matrix
- Solves: Manual site assignment pain
- Users: IT Admins
- Time Saved: ~30 minutes per bulk operation

**Future Tools** (using similar patterns):
- Technician-Group Matrix
- Technician-Role Matrix
- User-Account Matrix
- Asset-Site Matrix

## Performance

**Load Time:**
- 50 technicians × 30 sites = ~2 seconds
- 100 technicians × 50 sites = ~5 seconds

**Save Time:**
- Single technician: ~1 second
- Bulk (10 technicians): ~3-5 seconds

**Optimization:**
- Pagination (for 500+ technicians)
- Virtual scrolling
- Lazy loading
- Caching

## Future Enhancements

### Phase 1 (Next 2 weeks)
- [ ] Export matrix to CSV
- [ ] Import from CSV
- [ ] Undo/Redo functionality
- [ ] Change history log

### Phase 2 (Next month)
- [ ] Site grouping/categories
- [ ] Bulk selection (select all in column)
- [ ] Copy associations from one tech to another
- [ ] Template-based assignment

### Phase 3 (Future)
- [ ] Auto-assignment rules
- [ ] Approval workflow
- [ ] Audit trail
- [ ] Integration with AD groups

## Security Considerations

✅ **Implemented:**
- Login required
- Admin API key validation
- No direct database writes
- All changes via SDP API

⚠️ **Considerations:**
- Changes are immediate (no approval workflow)
- No change history/audit log (yet)
- No rollback capability (yet)

## Support

**For Tool Issues:**
- Check browser console for JavaScript errors
- Verify API credentials in Profile
- Test API endpoints with API Explorer first

**For SDP API Issues:**
- Review ME SDP API documentation
- Check API key permissions
- Contact SDP administrator

## Example Use Cases

### Use Case 1: New Technician Onboarding
1. Search for new technician
2. Check sites they need access to
3. Click "Save" on their row
4. Verify in SDP

### Use Case 2: Technician Transfer
1. Find technician changing roles
2. Uncheck old sites
3. Check new sites
4. Review changes
5. Save

### Use Case 3: Bulk Site Addition
1. Filter "Active Only"
2. Check new site column for all relevant techs
3. Review "Pending Changes" summary
4. "Save All Changes"

### Use Case 4: Access Audit
1. Review matrix visually
2. Look for unusual patterns
3. Technicians with too many sites?
4. Sites with too few technicians?
5. Make corrections as needed

---

**This tool embodies the SDP ecosystem philosophy:**
*"Fix SDP's UI/UX limitations with modern, efficient interfaces that save time and reduce errors"*
