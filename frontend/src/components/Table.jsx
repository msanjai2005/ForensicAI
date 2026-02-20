const Table = ({ columns, data, onRowClick }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-dark-border">
            {columns.map((col, idx) => (
              <th key={idx} className="text-left py-3 px-4 text-sm font-medium text-gray-400">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              onClick={() => onRowClick?.(row)}
              className={`border-b border-dark-border ${onRowClick ? 'hover:bg-dark-hover cursor-pointer' : ''}`}
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="py-3 px-4 text-sm">
                  {col.render ? col.render(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Table
