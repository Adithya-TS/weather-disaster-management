import GoogleLoginButton from '../components/auth/GoogleLoginButton';

const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8 p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Use your Google account to continue
          </p>
        </div>
        <div className="mt-8">
          <GoogleLoginButton />
        </div>
      </div>
    </div>
  );
};

export default Login;

