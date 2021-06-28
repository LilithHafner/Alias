println("Started")
using ImageView

new(h,w) = imshow(zeros(h,w))["gui"]["canvas"]
update! = imshow!

HEIGHT = 500
WIDTH = 800

canvas = new(HEIGHT, WIDTH)
img = zeros()
println("Entering Loop!")
while true
    update!(canvas, rand(HEIGHT, WIDTH))
    sleep(1/24)
end
