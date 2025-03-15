import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface FormData {
  question: string;
}

const QueryForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    setAnswer(null);

    try {
      const response = await axios.post('/api/v1/queries', {
        question: data.question,
        top_k: 4,
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Query error:', error);
      setAnswer('Error processing your query. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1">
            Ask a question about your documents
          </label>
          <textarea
            id="question"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="What information are you looking for?"
            {...register('question', { required: 'Question is required' })}
          />
          {errors.question && (
            <p className="mt-1 text-sm text-red-600">{errors.question.message}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : 'Submit Question'}
        </button>
      </form>

      {isLoading && (
        <div className="mt-6 text-center">
          <p className="text-primary-600">Generating answer...</p>
        </div>
      )}

      {answer && (
        <div className="mt-6 p-4 bg-white border border-gray-200 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Answer:</h3>
          <div className="prose max-w-none">
            <ReactMarkdown>{answer}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryForm; 