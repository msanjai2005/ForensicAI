const Badge = ({ children, variant = 'default' }) => {
  const variants = {
    default: 'bg-gray-700 text-gray-300',
    success: 'bg-green-900/50 text-green-400 border border-green-800',
    warning: 'bg-yellow-900/50 text-yellow-400 border border-yellow-800',
    danger: 'bg-red-900/50 text-red-400 border border-red-800',
    info: 'bg-blue-900/50 text-blue-400 border border-blue-800',
    purple: 'bg-purple-900/50 text-purple-400 border border-purple-800',
  }

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  )
}

export default Badge
