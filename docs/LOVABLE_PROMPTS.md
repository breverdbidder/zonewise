# ZoneWise Lovable Prompts

> Sequential prompts for building ZoneWise in Lovable.dev

## 📋 Pre-requisites

Before starting, ensure you have:
- [ ] Lovable.dev account
- [ ] GitHub repo `breverdbidder/zonewise` connected
- [ ] Supabase project created
- [ ] Mapbox account with token

---

## Prompt 01: Foundation

```
Create a modern React + TypeScript application called "ZoneWise" - an AI-powered zoning intelligence platform.

SETUP:
- Vite + React + TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Lucide React for icons

DESIGN SYSTEM:
- Primary color: #1E3A5F (navy)
- Accent color: #0D9488 (teal)
- Font: Inter for headings, system-ui for body
- Border radius: 8px for cards, 6px for buttons
- Clean, professional SaaS aesthetic

LAYOUT:
- Responsive sidebar navigation (collapsible on mobile)
- Header with logo, search, and user menu
- Main content area with max-width 1280px
- Footer with links

PAGES (create route structure):
1. Dashboard (/) - Welcome, quick search, stats
2. Map View (/map) - Placeholder for Mapbox
3. Districts (/districts) - List view placeholder
4. Settings (/settings) - User preferences

COMPONENTS:
- Sidebar with navigation links
- Header with ZoneWise logo (text-based for now)
- Card component for content sections
- Button variants (primary, secondary, ghost)

Make it look polished and professional. No placeholder "Lorem ipsum" - use realistic zoning-related content like "Search zoning districts", "273 districts verified", "17 jurisdictions".
```

---

## Prompt 02: Data Layer

```
Add Supabase integration to ZoneWise.

ENVIRONMENT VARIABLES:
- VITE_SUPABASE_URL
- VITE_SUPABASE_ANON_KEY

CREATE:

1. src/lib/supabase.ts - Supabase client initialization

2. src/types/index.ts with these TypeScript interfaces:
```typescript
interface Jurisdiction {
  id: string;
  name: string;
  county: string;
  state: string;
  municode_url: string | null;
  municode_verified: boolean;
}

interface ZoningDistrict {
  id: string;
  jurisdiction_id: string;
  code: string;
  name: string;
  description: string | null;
  color: string | null;
  regulations: {
    min_lot_size?: string;
    max_height?: string;
    setbacks?: {
      front?: string;
      side?: string;
      rear?: string;
    };
    far?: string;
  } | null;
  jurisdiction?: Jurisdiction;
}

interface UseType {
  id: string;
  district_id: string;
  use_name: string;
  category: 'residential' | 'commercial' | 'industrial' | 'institutional' | 'other';
  permitted: boolean;
  conditional: boolean;
  notes: string | null;
}
```

3. Custom hooks in src/hooks/:
- useJurisdictions() - Fetch all jurisdictions
- useZoningDistricts(jurisdictionId?: string) - Fetch districts, optionally filtered
- useDistrictDetails(districtId: string) - Fetch single district with uses
- useSearchDistricts(query: string) - Search by code or name

Each hook should:
- Return { data, isLoading, error }
- Handle loading states
- Handle errors gracefully
- Use TypeScript properly

4. Update Dashboard to show:
- Total districts count (from real data)
- Jurisdictions list
- Loading skeletons while fetching
```

---

## Prompt 03: Districts List

```
Build the Districts page (/districts) with a professional data table.

FEATURES:
1. Filterable table showing all zoning districts
2. Columns: Code, Name, Jurisdiction, Type (derived from code prefix)
3. Search input to filter by code or name
4. Jurisdiction dropdown filter
5. Sortable columns (click header to sort)
6. Pagination (20 items per page)

UI COMPONENTS:
- Search input with magnifying glass icon
- Dropdown select for jurisdiction filter
- Table with hover states on rows
- Sort indicators on headers (▲/▼)
- Pagination controls (prev/next, page numbers)
- Empty state when no results

INTERACTIONS:
- Click row to navigate to /districts/:id
- Debounced search (300ms)
- URL params for filters (shareable links)

LOADING STATES:
- Skeleton rows while loading
- Disabled pagination while loading

MOBILE:
- Cards instead of table on small screens
- Sticky search/filter bar

Use real data from Supabase via the useZoningDistricts hook.
```

---

## Prompt 04: District Detail

```
Build the District Detail page (/districts/:id) showing complete zoning information.

LAYOUT:
- Breadcrumb: Districts > [Jurisdiction] > [Code]
- Hero section with district code and name
- Two-column layout (main content + sidebar)

MAIN CONTENT:
1. Overview Card
   - Description
   - Jurisdiction name (with link)
   - Municode link (if available)

2. Regulations Card
   - Min lot size
   - Max building height
   - Setbacks (front, side, rear)
   - Floor Area Ratio (FAR)
   - Display as clean key-value pairs

3. Use Types Card
   - Grouped by category (Residential, Commercial, etc.)
   - Each use shows:
     - Name
     - ✅ Permitted / ⚠️ Conditional badge
     - Notes (expandable)
   - Color coding: green for permitted, amber for conditional

SIDEBAR:
1. Quick Stats
   - Total permitted uses count
   - Total conditional uses count

2. Related Districts
   - Other districts in same jurisdiction
   - List with links

3. Actions
   - "Save to favorites" button
   - "Share" button (copy link)
   - "Report issue" link

LOADING:
- Full page skeleton while loading
- 404 page if district not found

Fetch data using useDistrictDetails(id) hook.
```

---

## Prompt 05: Map Integration

```
Add Mapbox GL JS map to the Map View page (/map).

SETUP:
- Install mapbox-gl
- Use VITE_MAPBOX_TOKEN environment variable
- Import mapbox-gl CSS

LAYOUT:
- Split screen: Sidebar (320px) + Map (remaining)
- Sidebar collapsible on mobile (hamburger toggle)

SIDEBAR CONTENTS:
1. Search input (search districts by code/name)
2. Jurisdiction filter dropdown
3. District type filters (checkboxes):
   - Residential
   - Commercial
   - Industrial
   - Mixed Use
4. Results list (scrollable)
   - Show matching districts
   - Click to fly to location on map
   - Highlight selected district

MAP FEATURES:
1. Base style: mapbox://styles/mapbox/light-v11
2. Initial view: Florida state center
3. Navigation controls (zoom, compass)
4. Fullscreen control

INTERACTIONS:
- Hover on map: Show district code tooltip
- Click on map: Select district, show details popup
- Click result in sidebar: Fly to district, select it

POPUP CONTENT:
- District code and name
- Jurisdiction
- "View Details" button → navigates to /districts/:id

RESPONSIVE:
- Mobile: Map full screen, bottom sheet for sidebar
- Toggle button to show/hide sidebar

For now, add placeholder markers at jurisdiction center points since we don't have polygon data yet. We'll add real boundaries later.
```

---

## Prompt 06: Search & Dashboard

```
Enhance the Dashboard (/) with powerful search and useful widgets.

HERO SECTION:
- Large search bar (prominent, centered)
- Placeholder: "Search by district code, name, or use type..."
- Search icon + keyboard shortcut hint (⌘K)
- Auto-complete dropdown showing:
  - District matches
  - Jurisdiction matches
  - Use type matches

QUICK STATS ROW:
Four cards showing:
1. "273 Districts" - Total verified
2. "17 Jurisdictions" - Counties covered
3. "100% Verified" - Municode verification
4. "Updated Daily" - Data freshness

RECENT SEARCHES:
- Card showing last 5 searches (stored in localStorage)
- Click to re-run search
- "Clear history" link

FEATURED JURISDICTIONS:
- Grid of top jurisdictions (by district count)
- Each card shows:
  - Jurisdiction name
  - District count
  - "Explore" button

QUICK LINKS:
- "Browse All Districts"
- "View Map"
- "API Documentation" (placeholder)

KEYBOARD SHORTCUTS:
- ⌘K or /: Focus search
- Escape: Close search dropdown

Make the dashboard feel like a professional SaaS product landing page.
```

---

## Prompt 07: Polish & Deploy

```
Final polish and deployment preparation for ZoneWise.

GLOBAL IMPROVEMENTS:
1. Add page transitions (subtle fade)
2. Consistent loading states across all pages
3. Error boundaries with friendly error messages
4. 404 page for unknown routes
5. Meta tags for SEO (title, description per page)

ACCESSIBILITY:
- Focus visible states on all interactive elements
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels on icon-only buttons
- Skip to main content link

PERFORMANCE:
- Lazy load map component
- Virtualized list for districts (if > 100 items)
- Image optimization (if any images)

DARK MODE:
- Add dark mode toggle in header
- Persist preference in localStorage
- Tailwind dark: variants for all colors

MOBILE IMPROVEMENTS:
- Bottom navigation bar on mobile
- Pull-to-refresh on lists
- Swipe gestures where appropriate

FINAL CHECKS:
- Remove all console.logs
- Fix any TypeScript errors
- Verify all environment variables are used
- Test all routes work
- Check responsive at 375px, 768px, 1024px, 1440px

Build should pass with no errors: npm run build
```

---

## 🚀 Execution Order

1. **Prompt 01** → Get base structure
2. **Prompt 02** → Add data layer
3. **Prompt 03** → Build districts list
4. **Prompt 04** → Build detail page
5. **Prompt 05** → Add map
6. **Prompt 06** → Enhance dashboard
7. **Prompt 07** → Final polish

**Estimated Total Time:** 4-6 hours with Lovable

---

## 📝 After Each Prompt

1. Review the changes in Lovable
2. Test functionality
3. Check GitHub sync (Settings → GitHub)
4. Note any issues for next prompt

## 🔧 Troubleshooting

**Lovable not generating correctly?**
- Break prompt into smaller pieces
- Be more specific about component structure
- Reference existing components by name

**Build errors?**
- Check environment variables
- Verify imports are correct
- Ask Lovable to fix specific error
