import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/Tabs"
import { Mountain, Image, MoreVertical, Share2, Camera, Video, Paperclip } from 'lucide-react'
import React, { useState } from 'react'

export default function JourneyChat() {
  const [userInput, setUserInput] = useState('')
  const [responseData, setResponseData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Define the backend API URL
  const BACKEND_URL = 'http://127.0.0.1:5000/api/query'

  // Function to call the backend API
  const callBackendAPI = async (userInput: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userInput }),
      })

      const data = await response.json()
      setResponseData(data)
    } catch (error) {
      console.error('Error calling backend:', error)
      setResponseData({ error: 'An error occurred. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  // Handle form submission
  const handleSubmit = async () => {
    if (userInput.trim()) {
      // Call the backend API with the user's input
      await callBackendAPI(userInput)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-white">
      {/* Header */}
      <header className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-8">
          <h1 className="text-xl font-semibold text-green-500">Journey</h1>
          <Tabs defaultValue="book" className="w-[200px]">
            <TabsList>
              <TabsTrigger value="book" className="flex-1">Book</TabsTrigger>
              <TabsTrigger value="chat" className="flex-1">Chat</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon">
            <Image className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Share2 className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <MoreVertical className="h-5 w-5" />
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 p-4">
          <div className="flex h-full flex-col items-center justify-center text-center text-gray-500">
            <Mountain className="mb-4 h-16 w-16" />
            <p>Media</p>
            <p className="text-sm">No media available at the moment, try chatting with journey!</p>
          </div>
        </div>

        {/* Media Section */}
        <div className="w-64 border-l p-4">
          <div className="flex h-full flex-col">
            <div className="mb-4 flex justify-between">
              <h2 className="font-semibold">Media</h2>
              <Button variant="ghost" size="sm">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Mountain className="mx-auto mb-2 h-12 w-12 text-gray-400" />
                <p className="text-sm text-gray-500">No media available at the moment, try chatting with journey!</p>
              </div>
            </div>
            <div className="flex justify-center gap-2 pt-4">
              <Button variant="outline" size="icon">
                <Camera className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Video className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Paperclip className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </main>

      {/* Package Selection */}
      <div className="border-t p-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((package_num) => (
            <Card key={package_num} className="p-4">
              <h3 className="mb-2 font-medium">Package {package_num}</h3>
              <p className="text-sm text-gray-500">
                {package_num === 1 && "Explore a new city and discover the best local spots"}
                {package_num === 2 && "A guided adventure through mountains and valleys"}
                {package_num === 3 && "A flight to an exotic destination"}
                {package_num === 4 && "Relax in a luxury hotel with all the amenities"}
              </p>
            </Card>
          ))}
        </div>
        <div className="mt-4 flex gap-2">
          <Input
            placeholder="Type your message..."
            className="flex-1"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
          />
          <Button
            variant="solid"
            size="lg"
            onClick={handleSubmit}
            className="bg-green-500 hover:bg-green-600"
            disabled={isLoading}
          >
            {isLoading ? 'Submitting...' : 'Submit'}
          </Button>
        </div>
      </div>

      {/* Display Response */}
      {responseData && (
        <div className="border-t p-4">
          <h3 className="text-lg font-semibold">Response:</h3>
          <pre className="text-sm">{JSON.stringify(responseData, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}