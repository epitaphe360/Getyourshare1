import React from 'react';

export const SkeletonCard = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2"></div>
      </div>
      <div className="ml-4 w-12 h-12 bg-gray-200 rounded-lg"></div>
    </div>
  </div>
);

export const SkeletonTable = ({ rows = 5 }) => (
  <div className="animate-pulse">
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead className="bg-gray-50">
          <tr>
            {[1, 2, 3, 4, 5].map(i => (
              <th key={i} className="px-6 py-3">
                <div className="h-4 bg-gray-200 rounded w-20"></div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {Array.from({ length: rows }).map((_, index) => (
            <tr key={index}>
              {[1, 2, 3, 4, 5].map(i => (
                <td key={i} className="px-6 py-4">
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const SkeletonChart = () => (
  <div className="animate-pulse">
    <div className="h-64 bg-gray-200 rounded"></div>
  </div>
);

export const SkeletonDashboard = () => (
  <div className="space-y-8">
    {/* Header Skeleton */}
    <div className="flex justify-between items-start">
      <div>
        <div className="h-8 bg-gray-200 rounded w-64 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-96"></div>
      </div>
      <div className="flex space-x-3">
        <div className="h-10 bg-gray-200 rounded w-32"></div>
        <div className="h-10 bg-gray-200 rounded w-32"></div>
      </div>
    </div>

    {/* Stats Cards Skeleton */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </div>

    {/* Charts Skeleton */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <SkeletonChart />
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <SkeletonChart />
      </div>
    </div>

    {/* Table Skeleton */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <SkeletonTable rows={5} />
    </div>
  </div>
);

export default SkeletonDashboard;
