// Dashboard.jsx
import React from "react";
import { Link } from "react-router-dom";

export const Dashboard = () => {
  // Dummy data for demonstration
  const stats = [
    { name: 'Total Links', value: '1,248', change: '+12%', changeType: 'positive', href: '/links' },
    { name: 'Clicks Today', value: '324', change: '+8%', changeType: 'positive', href: '/analytics' },
    { name: 'Active Campaigns', value: '12', change: '+2', changeType: 'neutral', href: '/campaigns' },
    { name: 'Conversion Rate', value: '3.2%', change: '-0.4%', changeType: 'negative', href: '/analytics' }
  ];

  const recentActivities = [
    { id: 1, action: 'Link created', target: 'Summer Sale', time: '5 min ago', icon: '🔗' },
    { id: 2, action: 'Campaign updated', target: 'Winter Promotion', time: '1 hour ago', icon: '🎯' },
    { id: 3, action: 'New click', target: 'Product Page', time: '2 hours ago', icon: '👆' },
    { id: 4, action: 'Performance report', target: 'Monthly Analytics', time: '1 day ago', icon: '📊' }
  ];

  const quickActions = [
    { name: 'Create New Link', description: 'Generate a new shortened link', icon: '🔗', href: '/links/new', color: 'bg-blue-500' },
    { name: 'View Analytics', description: 'Check performance metrics', icon: '📈', href: '/analytics', color: 'bg-green-500' },
    { name: 'Manage Campaigns', description: 'Organize your campaigns', icon: '🎯', href: '/campaigns', color: 'bg-purple-500' },
    { name: 'Settings', description: 'Configure your account', icon: '⚙️', href: '/settings', color: 'bg-gray-500' }
  ];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Welcome back! Here's what's happening with your links today.</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/links/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <span className="mr-2">+</span>
            Create New Link
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="text-2xl font-bold text-gray-900">{item.value}</div>
                </div>
                <div className={`ml-2 w-0 flex-1 flex items-center justify-end text-sm font-medium ${
                  item.changeType === 'positive' ? 'text-green-600' : 
                  item.changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
                }`}>
                  {item.change}
                </div>
              </div>
              <div className="mt-1 text-sm text-gray-500">{item.name}</div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center">
                  <div className={`${action.color} rounded-md p-3 text-white`}>
                    <span className="text-lg">{action.icon}</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                      {action.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
              <Link to="/activity" className="text-sm text-blue-600 hover:text-blue-500">
                View all
              </Link>
            </div>
            <div className="flow-root">
              <ul className="-mb-8">
                {recentActivities.map((activity, activityIdx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {activityIdx !== recentActivities.length - 1 ? (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                            {activity.icon}
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-700">
                              {activity.action}{' '}
                              <span className="font-medium text-gray-900">
                                {activity.target}
                              </span>
                            </p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            {activity.time}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Performance Chart Placeholder */}
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Performance Overview</h2>
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <div className="text-gray-400 mb-2">📊</div>
              <p className="text-sm text-gray-500">Chart visualization will be implemented here</p>
              <Link
                to="/analytics"
                className="inline-block mt-4 text-sm text-blue-600 hover:text-blue-500"
              >
                View detailed analytics →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="bg-blue-50 rounded-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg font-medium text-blue-800">Need help getting started?</h3>
            <p className="mt-1 text-blue-700">Check out our documentation and guides</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link
              to="/support"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Visit Support Center
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};