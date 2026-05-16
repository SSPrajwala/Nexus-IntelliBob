import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
}

export default function LoadingState({ message = "Loading..." }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="w-8 h-8 text-red-500 animate-spin" />
      <p className="mt-4 text-sm text-gray-400">{message}</p>
    </div>
  );
}

// Made with Bob
