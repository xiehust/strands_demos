import json
import time
import asyncio



class StreamingQueue:
    """Simple async stream_queue for streaming responses."""
    
    def __init__(self,get_timeout=2):
        self._queue = asyncio.Queue()
        self._finished = False
        self._get_timeout = get_timeout
        
    async def put(self, item: str) -> None:
        """Add an item to the stream_queue."""
        if self._finished:
            self.reset()
        await self._queue.put(item)

    def reset(self) -> None:
        old_size = self._queue.qsize()
        self._finished = False
        # 清空队列
        cleared_count = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                cleared_count += 1
            except asyncio.QueueEmpty:
                break
            
    async def finish(self) -> None:
        """Mark the stream_queue as finished and add sentinel value."""
        self._finished = True
        await self._queue.put(None)

    async def stream(self):
        """Stream items from the stream_queue until finished."""
        while True:
            try:
                if self._get_timeout:
                    item = await asyncio.wait_for(
                        self._queue.get(), 
                        timeout=self._get_timeout
                    )
                else:
                    item = await self._queue.get()
                    
                if item is None and self._finished:
                    break
                yield item
            except asyncio.TimeoutError:
                # 可以选择继续等待或退出
                if self._finished:
                    break
                yield {"type":"heatbeat"}
                continue  
            

async def  process_stream_response(response):
        """Process the raw response from converse_stream"""
        last_yield_time = time.time()
        async for chunk in response:
            current_time = time.time()
            if current_time - last_yield_time > 0.1:  # 每100ms让出一次控制权，避免阻塞
                await asyncio.sleep(0.001)
                last_yield_time = current_time
            if 'message' in chunk:
                message = chunk['message']
                if message.get('role') == 'user' and message.get('content'):
                    content = message['content']
                    for content_block in content:
                        if 'toolResult' in content_block:
                            toolUseId = content_block['toolResult']['toolUseId']
                            yield {"type": "toolResult", "toolUseId":toolUseId,"data": content_block['toolResult']}
                    
            elif 'event' in chunk:
                event = chunk['event']
                # logger.info(event)
                # Handle message start
                if "messageStart" in event:
                    yield {"type": "message_start", "data": event["messageStart"]}
                    continue

                # Handle content block start
                if "contentBlockStart" in event:
                    block_start = event["contentBlockStart"]
                    yield {"type": "block_start", "data": block_start}
                    continue 

                # Handle content block delta
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]
                    yield {"type": "block_delta", "data": delta}
                    continue

                # Handle content block stop
                if "contentBlockStop" in event:
                    yield {"type": "block_stop", "data": event["contentBlockStop"]}
                    continue

                # Handle message stop
                if "messageStop" in event:
                    yield {"type": "message_stop", "data": event["messageStop"]}
                    continue

                # Handle metadata
                if "metadata" in event:
                    yield {"type": "metadata", "data": event["metadata"]}
                    continue     
                
            elif 'current_tool_use' in chunk:
                yield {"type": "tool_use", "data": chunk["current_tool_use"]}
                continue     
            
            elif 'result' in chunk:
                yield {"type": "metadata", "data": {"metrics":{"accumulated_metrics": chunk['result'].metrics.accumulated_metrics,
                       "accumulated_usage":chunk['result'].metrics.accumulated_usage}}}
                continue  
                
                
            
async def pull_queue_stream(stream_queue:StreamingQueue,model_id:str):
    current_content = ""
    thinking_start = False
    thinking_text_index = 0
    tooluse_start = False
    async for item in stream_queue.stream():
        event_data = {
            "id": f"chat{time.time_ns()}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_id,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": None
            }]
        }
        # 处理不同的事件类型
        if item["type"] == "messageStart":
            event_data["choices"][0]["delta"] = {"role": "assistant"}
            
        elif item["type"] == "block_start":
            block_start = item["data"]
            if "toolUse" in block_start.get("start", {}):
                event_data["choices"][0]["message_extras"] = {
                    "tool_name": block_start["start"]["toolUse"]["name"]
                }
            
        elif item["type"] == "block_delta":
            if "text" in item["data"]["delta"]:
                text = ""
                text += str(item["data"]["delta"]["text"])
                current_content += text
                event_data["choices"][0]["delta"] = {"content": text}
                thinking_text_index = 0
                
            if "toolUse" in item["data"]["delta"]:
                if not tooluse_start:    
                    tooluse_start = True
                event_data["choices"][0]["delta"] = {"toolinput_content": json.dumps(item["data"]["delta"]["toolUse"]['input'],ensure_ascii=False)}
                
            if "reasoningContent" in item["data"]["delta"]:
                if 'text' in item["data"]["delta"]["reasoningContent"]:
                    event_data["choices"][0]["delta"] = {"reasoning_content": item["data"]["delta"]["reasoningContent"]["text"]}

        elif item["type"] == "block_stop":
            if tooluse_start:
                tooluse_start = False
                event_data["choices"][0]["delta"] = {"toolinput_content": "<END>"}
        
        elif item["type"] in [ "message_stop" ,"result_pairs"]:
            event_data["choices"][0]["finish_reason"] = item["data"]["stopReason"]
            if item["data"].get("tool_results"):
                event_data["choices"][0]["message_extras"] = {
                    "tool_use": json.dumps(item["data"]["tool_results"],ensure_ascii=False)
                }
            if item["data"]["stopReason"] == 'end_turn':
                event_data = {
                    "id": f"stop{time.time_ns()}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model_id, 
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "end_turn"
                    }]
                }     
                yield f"data: [DONE]\n\n"     
                break
                # return
        # 发送事件
        # logger.info(event_data)
        yield f"data: {json.dumps(event_data)}\n\n"
        
        # 手动停止流式响应
        if item["type"] == "stopped":
            event_data = {
                "id": f"stop{time.time_ns()}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_id,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop_requested"
                }]
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            yield f"data: [DONE]\n\n"
            break