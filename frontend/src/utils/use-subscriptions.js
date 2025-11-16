import React, { useState } from "react";
import api from '../api'

export default function useSubscriptions () {
  const [ subscriptions, setSubscriptions ] = useState([])
  const [ subscriptionsPage, setSubscriptionsPage ] = useState(1)
  const [ subscriptionsCount, setSubscriptionsCount ] = useState(0)

  const removeSubscription = ({ id, callback }) => {
    api
      .deleteSubscriptions({ author_id: id })
      .then(res => {
        const subscriptionsUpdated = subscriptions.filter(item => {
          return item.id !== id
        })
        setSubscriptions(subscriptionsUpdated)
        setSubscriptionsCount(subscriptionsCount - 1)
        callback && callback()
      })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }
  
  return {
    subscriptions,
    setSubscriptions,
    subscriptionsPage,
    setSubscriptionsPage,
    removeSubscription,
    subscriptionsCount,
    setSubscriptionsCount
  }
}
