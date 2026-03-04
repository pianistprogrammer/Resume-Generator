<template>
    <div class="space-y-8">
        <!-- Header -->
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
                    User Management
                </h1>
                <p class="text-gray-600 dark:text-gray-400">
                    Manage all user accounts and permissions
                </p>
            </div>
        </div>

        <!-- Content -->
        <AdminUsers />
    </div>
</template>

<script setup lang="ts">
import { useAdminStore } from '~/stores/admin'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
    layout: 'admin',
    middleware: 'admin'
})

const adminStore = useAdminStore()
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
    // Check if user is admin
    if (authStore.user?.role !== 'admin') {
        router.push('/login')
        return
    }

    // Fetch users
    await adminStore.fetchUsers()
})
</script>
