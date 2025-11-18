const PageContainer = ({ children, title, description, actions }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {(title || description || actions) && (
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                {title && (
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                    {title}
                  </h1>
                )}
                {description && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {description}
                  </p>
                )}
              </div>
              {actions && <div className="mt-4 sm:mt-0 flex gap-2">{actions}</div>}
            </div>
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default PageContainer;

