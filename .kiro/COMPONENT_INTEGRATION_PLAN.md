# Component Integration Plan - Frontend Pages

## Overview
All 12 components have been created successfully, but pages are NOT using them. This document outlines the refactoring plan to integrate components into pages.

---

## 🎯 REFACTORING PRIORITY

### Phase 1: High-Impact Pages (2 pages)
These pages have the most complex logic and will benefit most from component reuse.

#### 1. JobSearchPage.vue
**Current State**: Custom filters, pagination, job display
**Components to Use**:
- SearchBar (for search + site selection)
- FilterPanel (for advanced filters)
- JobCard (for job display)
- Pagination (for page navigation)

**Changes Required**:
```vue
<!-- Replace custom search input with SearchBar -->
<SearchBar 
  v-model="searchQuery"
  :site="selectedSite"
  :filters="filters"
  @search="handleSearch"
/>

<!-- Replace custom filters with FilterPanel -->
<FilterPanel 
  :filters="filters"
  @filter-change="applyFilters"
/>

<!-- Replace custom job display with JobCard -->
<JobCard 
  v-for="job in jobs"
  :key="job.id"
  :job="job"
  :is-saved="isSaved(job.id)"
  @save="toggleSaveJob"
  @view-details="goToJobDetails"
/>

<!-- Replace custom pagination with Pagination -->
<Pagination 
  :current-page="currentPage"
  :page-size="pageSize"
  :total-items="totalJobs"
  @update:current-page="currentPage = $event"
  @update:page-size="pageSize = $event"
/>
```

#### 2. HomePage.vue
**Current State**: Hero section with custom search
**Components to Use**:
- SearchBar (for main search)
- StatsCard (for features section)

**Changes Required**:
```vue
<!-- Replace custom search with SearchBar -->
<SearchBar 
  v-model="searchQuery"
  @search="handleSearch"
/>

<!-- Replace feature cards with StatsCard -->
<StatsCard 
  label="بحث متقدم"
  value="1000+"
  subtitle="معايير بحث متقدمة"
/>
```

---

### Phase 2: Medium-Impact Pages (3 pages)
These pages need component integration for consistency.

#### 3. SavedJobsPage.vue
**Current State**: Stub/empty
**Components to Use**:
- JobCard (for saved jobs display)
- Pagination (for navigation)

**Implementation**:
```vue
<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">الوظائف المحفوظة</h1>
    
    <div v-if="savedJobs.length === 0" class="text-center py-12">
      <p class="text-gray-600">لم تحفظ أي وظائف بعد</p>
    </div>
    
    <div v-else class="space-y-4">
      <JobCard 
        v-for="job in savedJobs"
        :key="job.id"
        :job="job"
        is-saved
        @save="removeSavedJob"
        @view-details="goToJobDetails"
      />
    </div>
    
    <Pagination 
      :current-page="currentPage"
      :page-size="pageSize"
      :total-items="totalSavedJobs"
      @update:current-page="currentPage = $event"
    />
  </div>
</template>
```

#### 4. AlertsPage.vue
**Current State**: Stub/empty
**Components to Use**:
- AlertCard (for alert display)
- FormButton (for create alert button)

**Implementation**:
```vue
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold">التنبيهات</h1>
      <FormButton 
        label="إنشاء تنبيه جديد"
        @click="showCreateAlert = true"
      />
    </div>
    
    <div v-if="alerts.length === 0" class="text-center py-12">
      <p class="text-gray-600">لا توجد تنبيهات</p>
    </div>
    
    <div v-else class="space-y-4">
      <AlertCard 
        v-for="alert in alerts"
        :key="alert.id"
        :alert="alert"
        @edit="editAlert"
        @delete="deleteAlert"
        @toggle="toggleAlert"
      />
    </div>
  </div>
</template>
```

#### 5. ProfilePage.vue
**Current State**: Stub/empty
**Components to Use**:
- FormInput (for profile fields)
- FormButton (for save button)

**Implementation**:
```vue
<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold">الملف الشخصي</h1>
    
    <div class="bg-white rounded-lg p-6 space-y-4">
      <FormInput 
        v-model="profile.fullName"
        label="الاسم الكامل"
        placeholder="أدخل اسمك الكامل"
      />
      
      <FormInput 
        v-model="profile.email"
        label="البريد الإلكتروني"
        type="email"
        disabled
      />
      
      <FormInput 
        v-model="profile.phone"
        label="رقم الهاتف"
        placeholder="أدخل رقم هاتفك"
      />
      
      <FormButton 
        label="حفظ التغييرات"
        @click="saveProfile"
      />
    </div>
  </div>
</template>
```

---

### Phase 3: Authentication Pages (2 pages)
These pages need form components for consistency.

#### 6. LoginPage.vue
**Current State**: Stub/empty
**Components to Use**:
- FormInput (for email/password)
- FormButton (for submit)

**Implementation**:
```vue
<template>
  <div class="max-w-md mx-auto space-y-6">
    <h1 class="text-3xl font-bold text-center">تسجيل الدخول</h1>
    
    <form @submit.prevent="handleLogin" class="space-y-4">
      <FormInput 
        v-model="email"
        label="البريد الإلكتروني"
        type="email"
        placeholder="أدخل بريدك الإلكتروني"
        required
      />
      
      <FormInput 
        v-model="password"
        label="كلمة المرور"
        type="password"
        placeholder="أدخل كلمة المرور"
        required
      />
      
      <FormButton 
        label="تسجيل الدخول"
        type="submit"
        :loading="isLoading"
      />
    </form>
  </div>
</template>
```

#### 7. RegisterPage.vue
**Current State**: Stub/empty
**Components to Use**:
- FormInput (for form fields)
- FormCheckbox (for terms agreement)
- FormButton (for submit)

**Implementation**:
```vue
<template>
  <div class="max-w-md mx-auto space-y-6">
    <h1 class="text-3xl font-bold text-center">إنشاء حساب</h1>
    
    <form @submit.prevent="handleRegister" class="space-y-4">
      <FormInput 
        v-model="fullName"
        label="الاسم الكامل"
        placeholder="أدخل اسمك الكامل"
        required
      />
      
      <FormInput 
        v-model="email"
        label="البريد الإلكتروني"
        type="email"
        placeholder="أدخل بريدك الإلكتروني"
        required
      />
      
      <FormInput 
        v-model="password"
        label="كلمة المرور"
        type="password"
        placeholder="أدخل كلمة المرور"
        required
      />
      
      <FormCheckbox 
        v-model="agreeToTerms"
        label="أوافق على شروط الخدمة"
        required
      />
      
      <FormButton 
        label="إنشاء حساب"
        type="submit"
        :loading="isLoading"
      />
    </form>
  </div>
</template>
```

---

### Phase 4: Detail Pages (1 page)
These pages need full implementation.

#### 8. JobDetailsPage.vue
**Current State**: Stub/empty
**Components to Use**:
- FormButton (for save/apply buttons)
- StatsCard (for job stats)

**Implementation**:
```vue
<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="bg-white rounded-lg p-8 space-y-6">
      <!-- Job Header -->
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-4xl font-bold">{{ job.title }}</h1>
          <p class="text-xl text-gray-600">{{ job.company }}</p>
        </div>
        <FormButton 
          :label="isSaved ? 'محفوظة' : 'حفظ'"
          :variant="isSaved ? 'success' : 'outline'"
          @click="toggleSave"
        />
      </div>
      
      <!-- Job Stats -->
      <div class="grid grid-cols-3 gap-4">
        <StatsCard 
          label="الموقع"
          :value="job.location"
        />
        <StatsCard 
          label="نوع الوظيفة"
          :value="job.jobType"
        />
        <StatsCard 
          label="الراتب"
          :value="job.salary"
        />
      </div>
      
      <!-- Job Description -->
      <div>
        <h2 class="text-2xl font-bold mb-4">الوصف</h2>
        <p class="text-gray-700 whitespace-pre-wrap">{{ job.description }}</p>
      </div>
      
      <!-- Apply Button -->
      <FormButton 
        label="تقديم الطلب"
        @click="applyForJob"
      />
    </div>
  </div>
</template>
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: High-Impact (Week 1)
- [ ] Refactor JobSearchPage.vue
  - [ ] Replace custom search with SearchBar
  - [ ] Replace custom filters with FilterPanel
  - [ ] Replace custom job display with JobCard
  - [ ] Replace custom pagination with Pagination
  - [ ] Test all functionality
  
- [ ] Refactor HomePage.vue
  - [ ] Replace custom search with SearchBar
  - [ ] Replace feature cards with StatsCard
  - [ ] Test responsive design

### Phase 2: Medium-Impact (Week 2)
- [ ] Implement SavedJobsPage.vue
  - [ ] Add JobCard component
  - [ ] Add Pagination component
  - [ ] Connect to jobs store
  
- [ ] Implement AlertsPage.vue
  - [ ] Add AlertCard component
  - [ ] Add create alert form
  - [ ] Connect to alerts store
  
- [ ] Implement ProfilePage.vue
  - [ ] Add form components
  - [ ] Connect to user store

### Phase 3: Authentication (Week 2)
- [ ] Implement LoginPage.vue
  - [ ] Add form components
  - [ ] Connect to auth store
  
- [ ] Implement RegisterPage.vue
  - [ ] Add form components
  - [ ] Add validation
  - [ ] Connect to auth store

### Phase 4: Details (Week 3)
- [ ] Implement JobDetailsPage.vue
  - [ ] Add job details display
  - [ ] Add save/apply buttons
  - [ ] Connect to jobs store

---

## 🧪 TESTING CHECKLIST

For each refactored page:
- [ ] Component renders correctly
- [ ] All props are passed correctly
- [ ] All events are emitted correctly
- [ ] Responsive design works (mobile, tablet, desktop)
- [ ] Dark mode works
- [ ] RTL (Arabic) layout works
- [ ] Accessibility is maintained
- [ ] No console errors

---

## 📊 EXPECTED OUTCOMES

### Code Quality Improvements
- ✅ Reduced code duplication
- ✅ Improved maintainability
- ✅ Consistent styling and behavior
- ✅ Better component reusability
- ✅ Easier testing

### Performance Improvements
- ✅ Smaller bundle size (component reuse)
- ✅ Faster development (component reuse)
- ✅ Better caching (component optimization)

### User Experience Improvements
- ✅ Consistent UI/UX across pages
- ✅ Better accessibility
- ✅ Improved responsiveness
- ✅ Better dark mode support

---

## 📝 NOTES

1. **Component Props**: Ensure all components have proper TypeScript types
2. **Event Handling**: Use proper event naming conventions (kebab-case)
3. **Styling**: Ensure Tailwind CSS classes are consistent
4. **Accessibility**: Add ARIA labels and keyboard navigation
5. **i18n**: Ensure all text is translatable
6. **RTL Support**: Test with Arabic text and RTL layout
