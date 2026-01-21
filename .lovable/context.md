# ZoneWise - Lovable Project Context

## Project Overview

ZoneWise is an AI-powered zoning intelligence platform that helps real estate professionals, developers, and investors understand zoning regulations across Florida.

**Key Value Proposition:** Answer "Can I build X at location Y?" in seconds.

## Design System

### Colors
```css
--primary: #1E3A5F;      /* Navy - headers, primary actions */
--accent: #0D9488;       /* Teal - highlights, links */
--background: #FFFFFF;   /* White - main background */
--surface: #F9FAFB;      /* Gray-50 - cards, sections */
--text: #1F2937;         /* Gray-800 - body text */
--text-muted: #6B7280;   /* Gray-500 - secondary text */
--border: #E5E7EB;       /* Gray-200 - borders */
--success: #10B981;      /* Green - permitted uses */
--warning: #F59E0B;      /* Amber - conditional uses */
--error: #EF4444;        /* Red - prohibited uses */
```

### Typography
- **Headings:** Inter, font-weight 600-700
- **Body:** System UI / Inter, font-weight 400
- **Code:** JetBrains Mono / monospace

### Spacing
- Base unit: 4px
- Common: 8px, 12px, 16px, 24px, 32px, 48px

### Border Radius
- Cards: 8px
- Buttons: 6px
- Inputs: 4px
- Modals: 12px

### Shadows
```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
```

## Component Patterns

### Layout
- Use CSS Grid for page layouts
- Flexbox for component-level alignment
- Max content width: 1280px
- Responsive breakpoints: sm(640), md(768), lg(1024), xl(1280)

### Cards
```jsx
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  {/* Card content */}
</div>
```

### Buttons
```jsx
// Primary
<button className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90">

// Secondary
<button className="bg-white text-primary border border-primary px-4 py-2 rounded-md hover:bg-gray-50">

// Ghost
<button className="text-gray-600 px-4 py-2 rounded-md hover:bg-gray-100">
```

### Forms
```jsx
<input 
  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary/20 focus:border-primary"
/>
```

## Data Integration

### Supabase Client
All data fetching should use the Supabase client from `src/lib/supabase.ts`:

```typescript
import { supabase } from '@/lib/supabase';

const { data, error } = await supabase
  .from('zoning_districts')
  .select('*');
```

### Custom Hooks
Create hooks in `src/hooks/` for data fetching:
- `useZoningDistricts()` - List all districts
- `useDistrictDetails(id)` - Single district
- `useJurisdictions()` - List jurisdictions
- `useUsageTypes(districtId)` - Uses for a district

### Loading States
Always show loading indicators:
```jsx
{isLoading ? (
  <div className="animate-pulse bg-gray-200 h-4 rounded" />
) : (
  <span>{data}</span>
)}
```

### Error Handling
Display user-friendly errors:
```jsx
{error && (
  <div className="bg-red-50 text-red-700 p-4 rounded-md">
    {error.message}
  </div>
)}
```

## Map Integration

### Mapbox Setup
```jsx
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;
```

### District Layers
- Residential: Blue tones (#3B82F6)
- Commercial: Purple tones (#8B5CF6)
- Industrial: Orange tones (#F97316)
- Mixed Use: Teal tones (#14B8A6)

### Interactions
- Hover: Highlight district, show tooltip
- Click: Open detail panel
- Double-click: Zoom to district

## Pages Structure

### Dashboard (/)
- Search bar (prominent)
- Quick stats cards
- Recent searches
- Featured districts

### Map View (/map)
- Full-width map
- Collapsible sidebar with filters
- District list (scrollable)
- Detail panel (slide-in)

### Districts (/districts)
- Filterable table
- Sort by jurisdiction, code, type
- Quick view modal
- Export to CSV

### District Detail (/districts/:id)
- Overview section
- Regulations table
- Use types (permitted/conditional)
- Related districts
- Location map

## File Organization

```
src/
├── components/
│   ├── ui/           # Base UI components
│   ├── layout/       # Header, Sidebar, Footer
│   ├── maps/         # Map-related components
│   └── districts/    # District-specific components
├── hooks/
│   ├── useZoningDistricts.ts
│   ├── useDistrictDetails.ts
│   └── useMapLayers.ts
├── pages/
│   ├── Dashboard.tsx
│   ├── MapView.tsx
│   ├── Districts.tsx
│   └── DistrictDetail.tsx
├── lib/
│   ├── supabase.ts
│   └── utils.ts
└── types/
    └── index.ts
```

## Important Notes

1. **Never hardcode data** - Always fetch from Supabase
2. **Mobile-first** - Design for mobile, enhance for desktop
3. **Accessibility** - Use semantic HTML, ARIA labels
4. **Performance** - Lazy load maps, virtualize long lists
5. **TypeScript** - Full type coverage required

## Environment Variables

These must be set in Lovable's environment settings:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_MAPBOX_TOKEN`
