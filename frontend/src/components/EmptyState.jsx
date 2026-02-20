const EmptyState = ({ icon, title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && <div className="text-gray-600 mb-4">{icon}</div>}
      <h3 className="text-lg font-medium text-gray-300 mb-2">{title}</h3>
      {description && <p className="text-gray-500 mb-4">{description}</p>}
      {action}
    </div>
  )
}

export default EmptyState
