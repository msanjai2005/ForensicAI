const Card = ({ children, className = '', hover = false }) => {
  return (
    <div className={`card ${hover ? 'hover:bg-dark-hover cursor-pointer' : ''} ${className}`}>
      {children}
    </div>
  )
}

export default Card
