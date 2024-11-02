
1. Admin Functionalities:
```
- Authentication:
  - Sign up (with school details)
  - Sign in
  - Sign out
  - Password reset
  - Profile management

- Teacher Management:
  - Create teacher accounts(with a default password)
  - View teacher list
  - Edit teacher details
  - Deactivate teacher accounts

- Student Management:
  - Create student profiles
  - View student list
  - Edit student details
  - Assign/remove courses

- Course Management:
  - Create courses
  - Assign teachers to courses
  - View course list
  - Edit course details

- Attendance Management:
  - View attendance calendar
  - View daily attendance reports
  - Export attendance data
```

2. Teacher Functionalities:
```
- Authentication:
  - Sign in
  - Sign out
  - Password management
  - Profile updates

- Course Management:
  - View assigned courses
  - View student lists per course

- Attendance Management:
  - Take daily attendance
  - View attendance history
  - Update attendance records
  - Generate reports
```

3. Template Structure and Design:

```
templates/
├── auth/
│   ├── login.html                 # Modern login form with email/password
│   ├── signup.html               # Admin signup with school details
│   ├── password_reset.html       # Password reset flow
│   └── onboarding/              # Admin onboarding wizard
│       ├── school_details.html
│       └── preferences.html
│
├── dashboard/
│   ├── admin/
│   │   ├── index.html           # Stats, recent activities, quick actions
│   │   ├── teachers/
│   │   │   ├── list.html        # Teacher management with filters
│   │   │   └── form.html        # Create/edit teacher
│   │   ├── students/
│   │   │   ├── list.html        # Student management with filters
│   │   │   └── form.html        # Create/edit student
│   │   ├── courses/
│   │   │   ├── list.html        # Course management
│   │   │   └── form.html        # Create/edit course
│   │   └── attendance/
│   │       ├── calendar.html     # Calendar view of attendance
│   │       └── daily_view.html   # Daily attendance details
│   │
│   └── teacher/
│       ├── index.html           # Course overview, recent activities
│       ├── profile.html         # Profile management
│       └── attendance/
│           ├── course_select.html # Select course for attendance
│           └── mark.html         # Mark attendance for selected course
```

Design Guidelines:
1. Modern UI Components:
   - Clean, minimal design with ample white space
   - Card-based layout for dashboard widgets
   - Soft shadows and rounded corners
   - Subtle animations for interactions
   - Responsive design for all screen sizes

2. Color Scheme:
   - Primary: Deep blue (#1a73e8)
   - Secondary: Teal (#00796b)
   - Accent: Orange (#ff6d00)
   - Background: Light gray (#f8f9fa)
   - Text: Dark gray (#202124)

3. Dashboard Features:
   - Sticky header with quick actions
   - Collapsible sidebar navigation
   - Real-time notifications
   - Interactive charts and statistics
   - Quick filters and search
   - Skeleton loading states
   - Toast notifications for actions

4. Special Components:
   - Calendar view with heat map for attendance
   - Progress tracking cards
   - Student profile cards with avatars
   - Quick action floating buttons
   - Modal forms for quick edits
   - Drag-and-drop course assignment

