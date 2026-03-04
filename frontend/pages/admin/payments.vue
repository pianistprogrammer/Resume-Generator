<template>
    <div class="space-y-8">
        <!-- Header -->
        <div>
            <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
                Payment Management
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
                View and manage user payments and transactions
            </p>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="stat-card">
                <div class="flex items-center justify-between mb-4">
                    <CreditCard :size="32" class="text-emerald-400" />
                    <span class="text-emerald-400 text-xs font-medium">TOTAL</span>
                </div>
                <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    $0
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Total Revenue</div>
            </div>

            <div class="stat-card">
                <div class="flex items-center justify-between mb-4">
                    <TrendingUp :size="32" class="text-blue-400" />
                    <span class="text-blue-400 text-xs font-medium">THIS MONTH</span>
                </div>
                <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    $0
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Monthly Revenue</div>
            </div>

            <div class="stat-card">
                <div class="flex items-center justify-between mb-4">
                    <Users :size="32" class="text-purple-400" />
                    <span class="text-purple-400 text-xs font-medium">CUSTOMERS</span>
                </div>
                <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    0
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Paying Customers</div>
            </div>
        </div>

        <!-- Payments Table -->
        <div class="glass-card p-6">
            <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                Recent Transactions
            </h2>

            <div class="text-center py-12">
                <CreditCard :size="64" class="text-gray-600 mx-auto mb-4" />
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    No payments yet
                </h3>
                <p class="text-gray-600 dark:text-gray-400">
                    Payment transactions will appear here once users start purchasing credits
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { CreditCard, TrendingUp, Users } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
    layout: 'admin',
    middleware: 'admin'
})

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
    // Check if user is admin
    if (authStore.user?.role !== 'admin') {
        router.push('/login')
    }
})
</script>
