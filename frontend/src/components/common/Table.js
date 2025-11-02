import React, { memo, useMemo } from 'react';

const Table = memo(({ columns = [], data = [], onRowClick }) => {
  // Memoize empty state to prevent re-renders
  const emptyState = useMemo(() => (
    <tr>
      <td colSpan={columns.length} className="px-6 py-8 text-center text-gray-500">
        Aucune donnée disponible
      </td>
    </tr>
  ), [columns.length]);

  // Ensure data is always an array
  const safeData = Array.isArray(data) ? data : [];

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {safeData.length === 0 ? (
            emptyState
          ) : (
            safeData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick && onRowClick(row)}
                className={onRowClick ? 'hover:bg-gray-50 cursor-pointer' : ''}
              >
                {columns.map((column, colIndex) => (
                  <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {column.render ? column.render(row) : row[column.accessor]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
});

Table.displayName = 'Table';

export default Table;
